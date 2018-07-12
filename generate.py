import sys

global tab
tab = '	'

f= open("dg.html","r+")
file = f.read()

story = file.split('<tw-storydata')
story = story[1].split('</tw-storydata')
data = story[0]

data = data.replace('&quot;','"')
data = data.replace('&#39;',"'")
data = data.replace('UserOptions','\nUserOptions')
data = data.replace('name="','\nname="')
data = data.replace('tags="','\ntags="')
data = data.replace('">','">\n')
data = data.replace('<tw-passagedata','\n<tw-passagedata')
data = data.replace('</tw-passagedata>','\n</tw-passagedata>')
outfile = open("geneated.cs","w+")
outfile.write(data)

blocks = data.split('<tw-passagedata')
passages = []

parsed = ''
generated = ''
embedded_variables = []

for i in range(1, len(blocks)):
    if '$IsRandom' in blocks[i]:
        blocks[i] = blocks[i] + '\n\nRandomBlockHook'
    if '$IsConditional' in blocks[i]:
        blocks[i] = blocks[i] + '\n\nConditionalBlockHook'   
    if '$IsSpecific' in blocks[i]:
        blocks[i] = blocks[i] + '\n\nSpecificBlockHook' 
    passages.append(blocks[i])


logic_node_counter = 0
new_passages = []
for p in passages:
    new_passage = ''
    p = p.replace('</tw-passagedata>','')

    if 'tags="red"' in p:
        logic_node_counter = logic_node_counter + 1
        blocks = p.split('\n\n')
        lines = p.split('\n')
        #process line by line
        #process block by block
        counter = 0
        child_nodes = []

        for line in lines:
            if 'name="' in line:
                new_line = line.replace('name="','if( $currentNode == "')
                new_line = new_line + ' ){\n'
                new_passage = new_passage + new_line + '\n'                        

        for block in blocks: 
            block_lines = block.split('\n')
            for l in block_lines:
                if 'UserOptions' in l:
                    n_options = l.replace('UserOptions:','')
                    for i in range(10):
                        n_options = n_options.replace(' ','')
            responses = []

            if '$IsRandom' in block and '$IsSpecific' in block and '$IsConditional' in block:
                is_lines = block.split('\n')
                for l in is_lines:
                    if 'UserOptions' not in l:
                        l = l.replace("_value_",'false')
                        words = l.split(' ')
                        if '$IsSpecific' in l:
                            for i in range(10):
                                l = l.replace(' ','')
                            if '{}' in l:
                                is_prob = False
                                words[3] = 'false'
                            else:
                                is_prob = True
                                words[3] = 'true'
                                tokens = l.split('{')
                                tokens = tokens[1].split('}')
                                token = tokens[0]
                                new_probs = []
                                probs = token.split(',')
                                for prob in probs:
                                    prob = float(prob)
                                    prob = prob * 10
                                    prob = str(prob)
                                    prob = prob.split('.')[0]
                                    new_probs.append(prob)
                        new_line = tab + words[1] + ' = ' + words[3].replace(')','') + ';\n'
                        new_passage = new_passage + new_line


            if 'UserResponse' in block and 'if:' not in block:
                flags = []
                counter = counter + 1
                response = block 
                response = response.replace(' is not ', ' != ')
                response = response.replace(' is ', ' == ')
                response_lines = response.split('\n')
                for l in response_lines:
                    if 'UserResponse' not in l:
                        words = l.split(' ')
                        parameter = words[0].replace('(','')
                        operator = words[1]
                        value = words[2].replace(')','')
                        if '"_value_"' in l:
                            new_line = tab + parameter + 'Flag' + str(counter) + ' = ' + 'true;\n'
                            flags.append(parameter + 'Flag' + str(counter))
                        elif 'MicSpeech' in l:
                            baked = ''
                            sentences = ''
                            l = l.split(' == ')[1]
                            l = l.replace('"','')
                            l = l.replace(')','')
                            l = l.replace('(','')
                            sentences = l.split('//')
                        
                            baked = '\ttoCompare.Clear();\n\t' + 'toCompare.Add(MicSpeech);' +'\n\t'
                            for s in sentences:
                                baked = baked + 'toCompare.Add("' + s + '");' +'\n\t'
                            baked = baked + 'if( SimilarityCheck(toCompare) == true ){\n\t\tMicSpeechFlag' + str(counter) + ' = ' + 'true;\n\t}\n'
                            flags.append('MicSpeechFlag' + str(counter))
                            new_line = baked
                        else:
                            new_line = tab + 'if( ' + parameter + ' ' + operator + ' ' + value + ' )' + '{ ' + parameter + 'Flag' + str(counter) + ' = ' + 'true; }\n' 
                            flags.append(parameter + 'Flag' + str(counter))
                        new_passage = new_passage + new_line
                #print(flags)
                k = 0
                new_line = '\tif( '
                while k < len(flags) - 1:
                    new_line = new_line + flags[k] + ' && '
                    k = k + 1
                new_line = new_line + flags[len(flags)-1] + ' ){ UserResponse' + str(counter) + ' = true; }\n'
                #print(new_line)
                new_passage = new_passage + new_line
            #if '[[' in block:
                #print(block)
            if 'UserResponse' in block and '[ [[' in block:
                c_lines = block.split('\n')
                for l in c_lines:
                    child_node = l.split('[ [[')
                    child_node = '"' + child_node[1].replace(']] ]','"')
                    child_nodes.append(child_node)

            if 'RandomBlockHook' in block:
                new_line = ''
                str1 =  '\n\tif( $IsRandom == true){\n\t\tstring[] options' + str(logic_node_counter) +  ' = new string['+ n_options +'];\n\t\t'
                i = 0
                for child in child_nodes:
                    str1 =  str1 + 'options' + str(logic_node_counter) + '['+ str(i) +'] = ' + child + ';\n\t\t'
                    i = i + 1
                str2 = '$currentNode = options'+ str(logic_node_counter) + '[Random.Range(0,options' + str(logic_node_counter) +'.Length)];\n\t}\n\n'
                new_line = tab + str1 + str2
                new_passage = new_passage + new_line

            if 'SpecificBlockHook' in block and is_prob:
                new_line = ''
                str1 =  '\n\tif( $IsSpecific == true){\n\t\tstring[] specifics' + str(logic_node_counter) +  ' = new string[10];\n\t\t' 
                i = 0
                str1 = str1 + 'int index' + str(logic_node_counter) +' = 0;' +'\n\n\t\t'
                for prob in new_probs:
                    i = i + 1
                    str1 = str1 + 'int prob' + str(i) +  '_' + str(logic_node_counter) + ' = '+ prob + ';\n\t\t' + 'int counter'+ str(i) +  '_' + str(logic_node_counter) + ' = 0;'+'\n\t\t'
                    while_loop = '\n\t\twhile ( counter' + str(i) + '_' + str(logic_node_counter)+ ' < prob'+  str(i) + '_' + str(logic_node_counter) + ')  {\n\t\t\tspecifics' + str(logic_node_counter) + '[index'+ str(logic_node_counter) +'] = ' + child_nodes[i-1]+ ';\n\t\t\tcounter' + str(i) + '_' + str(logic_node_counter) + '++;' +'\n\t\t\tindex'+ str(logic_node_counter) + ' = index' + str(logic_node_counter)+ ' + 1;\n\t\t}\n\n\t\t'
                    str1 = str1 + while_loop
                str2 = '$currentNode = specifics'+str(logic_node_counter)+'[Random.Range(0,10)];\n\t}\n'
                new_line = tab + str1 + str2 
                new_passage = new_passage + new_line

            if 'ConditionalBlockHook' in block:
                new_line = ''
                i = 0
                for child in child_nodes:
                    i = i + 1
                    str1 = '\tif( $IsConditional && $UserResponse' + str(i) + ' == true )' + '{\n\t' + tab + '$currentNode = ' + child + '; \n\t}\n' 
                    new_line = new_line + str1
                new_passage = new_passage + new_line
            '''
            if 'OpenConv:' in block: 
                lines = block.split('\n')
                for line in lines:
                    if '$Duration' in line:
                        if '"' in line:
                            duration_str = line.split('"')[1]
                            duration_str = '"'+duration_str+'"'
                        else:
                            duration_str = line.split(' is ')[1]
                            duration_str = '"'+duration_str+'"'
                    if 'start:' in line and '[[' in line:
                        startNode = line.split('[[')[1]
                        startNode = startNode.split(']]')[0]
                    if 'end:' in line and '[[' in line:
                        endNode = line.split('[[')[1]
                        endNode = endNode.split(']]')[0]                    


                new_line = '\tif (IsOpen == true) {\n\t\tcurrentNode = ' + startNode + ';\n\t\tnextNode = ' + endNode + ';\n\t\tduration = ' + duration_str + ';\n\t\tdur = 0;\n\t\tif (Int32.TryParse(duration, out dur) == false){\n\t\t\tif (duration == "random") {\n\t\t\t\tdur = rnd.Next (1, 10);\n\t\t\t}\n\t\t\telse if (duration == "low") {\n\t\t\t\tdur = rnd.Next (1, 10);\n\t\t\t}\n\t\t\telse if (duration == "high") {\n\t\t\t\tdur = rnd.Next (1, 10);\n\t\t\t}\n\t\t\telse (duration == "medium") {\n\t\t\t\tdur = rnd.Next (1, 10);\n\t\t\t}\n\t\t}\n\t}\n'
                new_passage = new_passage + new_line + '\n'
                
                #print(startNode,endNode,duration_str)
            '''
        new_passage = new_passage + '\n\t$IsAvatarNode = false;'   
        new_passage = new_passage + '\n}\n'        
        generated = generated + new_passage + '\n'


    if 'tags="green"' in p:
        blocks = p.split('\n\n')
        lines = p.split('\n')
        seen  = False
        for line in lines:
            
            if 'name="' in line:
                new_line = line.replace('name="','if( $currentNode == "')
                new_line = new_line + ' ){\n'
                new_passage = new_passage + new_line + '\n'

            if '[[' in line:
                seen = True
                l = line.replace('_NextNodeTitle_','NONE')
                l = l.replace('[[','"')
                l = l.replace(']]','"')
                new_line = '$currentNode = ' + l + ';'
                new_passage = new_passage + tab + new_line + '\n'   
        
        if seen == False:
            new_line = '$currentNode = "NONE";'
            new_passage = new_passage + tab + new_line + '\n'
        
        new_passage = new_passage + '\n\t$IsAvatarNode = false;'        
        new_passage = new_passage + '\n}\n'
        generated = generated + new_passage + '\n'
        #print(new_passage)      
        #for line in lines: 
            #if '[[' in line:
                #print(line)  
    
    if 'tags="blue"' in p:
        new_passage = ''
        p = p.replace('tags="','\ntags="')
        blocks = p.split('\n\n')
        lines = p.split('\n')
        #process line by line
        #process block by block

        for block in blocks: 
            new_block = ''
            if 'name="' in block:
                lines = block.split('\n')
                new_line = ''
                for l in lines:
                    if 'name="' in l:
                        if 'pid="1"' in p:
                            new_line = l.replace('name="','if( $currentNode == "')
                            new_line = 'if( $currentNode == "START" ){\n'
                            new_passage = new_passage + new_line + '\n'                            
                        else:
                            new_line = l.replace('name="','if( $currentNode == "')
                            new_line = new_line + ' ){\n'
                            new_passage = new_passage + new_line + '\n'
                    

            if 'Avatar' in block and 'name="' not in block:
                lines  = block.split('\n')
                new_line = ''

                for l in lines:
                    if 'Avatar1:' in l:
                        for i in range(10):
                            l = l.replace(' ','')

                    if 'Avatar2:' in l:
                        for i in range(10):
                            l = l.replace(' ','')                    

                    if '(set: $' in l:
                        words = l.split(' ')
                        words[3] = words[3].replace('_ID_', 'NONE')
                        words[3] = words[3].replace(')','')
                        new_line = words[1] + ' = ' + words[3].replace('_ID_', 'NONE') + ';'
                        new_passage = new_passage + tab + new_line + '\n'
                    
            if 'Scene:' in block:
                lines = block.split('\n')
                new_line = ''
                for l in lines:
                    if '(set: $' in l:
                        words = l.split(' ')
                        words[3] = words[3].replace('_ID_', 'NONE')
                        words[3] = words[3].replace(')','')
                        new_line = words[1] + ' = ' + words[3].replace('_ID_', 'NONE') + ';'
                        new_passage = new_passage + tab + new_line + '\n'                       

            if '[[' in block and ']]' in block and  '_NextNodeTitle_' not in block:
                b = block.replace('[[','"')
                b = b.replace(']]','"')
                new_line = 'nextNode = ' + b + ';'
                new_passage = new_passage + tab + new_line + '\n'

 

        p = p.replace('Avatar1:\n','$Avatar1NextText = ')
        p = p.replace('Avatar2:\n','$Avatar2NextText = ')
             
        #last line by line visit
        ls = p.split('\n')
        for l in ls:
            if '$Avatar1NextText = ' in l:
                tokens = l.split('$Avatar1NextText = ')[1].split(' ')
                new_line = ''
                for t in tokens:
                    if '$' in t:
                
                        for j in range(10):
                            t = t.replace('!','')
                            t = t.replace('?','')
                            t = t.replace(',','')
                        
                    if '"$' in t:
                        t.replace('"$','')
                        t = t + ' + "'

                    if '$' in t and '"' in t:
                        t = t.replace('$', '+ ')
                        t = t.replace('"','' )
                        t = '" ' + t
                    if '$' in t and '"' not in t:
                        t = '" + ' + t + ' + "'
                    
                    
                    new_line = new_line + ' ' + t
                    
                
                for t in tokens:
                    if '$' in t:
                        for j in range(10):
                            t = t.replace('$','')
                            t = t.replace('(','')
                            t = t.replace(')','')
                            t = t.replace('"','')
                            t = t.replace(';','')
                            t = t.replace('!','')
                            t = t.replace('?','')
                            t = t.replace(',','')
                        if t not in embedded_variables:
                            embedded_variables.append(t)



                new_line = '$Avatar1NextText = ' + new_line + ';'
                new_line = new_line.replace('_Insert Avatar1 Dialogue Here_','NONE')
                new_passage = new_passage + tab + new_line + '\n'
            if '$Avatar2NextText = ' in l:
                tokens = l.split('$Avatar2NextText = ')[1].split(' ')
                new_line = ''
                for t in tokens:
                    if '"$' in t:
                        t.replace('"$','')
                        t = t + ' + "'
                    if '$' in t and '"' in t:
                        t = t.replace('$', '+ $')
                        t = t.replace('"','' )
                        t = '" ' + t
                    if '$' in t and '"' not in t:
                        t = '" + ' + t + ' + "'
                    new_line = new_line + ' ' + t

                new_line = '$Avatar2NextText = ' + new_line + ';'
                new_line = new_line.replace('_Insert Avatar2 Dialogue Here_','NONE')
                new_passage = new_passage + tab + new_line + '\n'
            
        new_passage = new_passage + '\n\t$IsAvatarNode = true;'
        new_passage = new_passage + '\n}\n'
        generated = generated + new_passage + '\n'
        #print(new_passage)



variables = []
ls = generated.split('\n')
for l in ls:
    tokens = l.split('\t')
    for t in tokens:
        words = t.split(' ')
        for w in words:
            if '$' in w and w not in variables:
                variables.append(w)

other = ''
booleans = ''
avatar_variables = ''
scene_variables = ''

toAdd = ''


for v in variables:        
    if ('Flag' not in v and 'AnalysisBasic' in v) or ('Flag' not in v and 'AnalysisCustom' in v):
        v = v.replace('$','')
        if 'AnalysisBasic' in v:
            toAdd = toAdd + 'bool ' + v + ' = ' + 'GetComponent<Controller>().user.traits.'+ v.split('AnalysisBasic')[1].lower() + '.has_trait.ToString();\n'
        if 'AnalysisCustom' in v:
            toAdd = toAdd + 'bool ' + v + ' = ' + 'GetComponent<Controller>().user.traits.'+ v.split('AnalysisCustom')[1].lower() + '.has_trait.ToString();\n'    
    elif v.replace('$','') not in embedded_variables:
        v = v.replace(';','')
        if '$Is' in v or 'Flag' in v or 'UserResponse' in v:
            booleans = booleans + v.replace('$','bool ') + ' = false;\n'
        elif 'Avatar' in v:
            avatar_variables = avatar_variables + v.replace('$','string ') + ' = "NONE";\n'
        elif 'SceneRendering' in v or 'SceneLighting' in v or  'SceneSound' in v or  'NarratorSound' in v or  'Screen' in v:
            scene_variables = scene_variables + v.replace('$','string ') + ' = "NONE";\n'
    
        else:
            other = other + v.replace('$','string ') + ' = "";\n'
    
#add emmbeded variables...
embedded = ''
j = 2 
for e in embedded_variables:
    j = j + 1
    #print(e)
    embedded = embedded + 'string ' + e + ' = ' + 'dialogueInput[' + str(j) +'];\n'


basic_info = ["first_name","last_name","email_address","server_name","email_handle","gender","location","hometown"]
basic = ''
for e in embedded_variables:
    for b in basic_info:
        if b == e:
            new_line = 'string ' + e + ' = GetComponent<Controller>().user.'+ e +';'
            basic = basic + new_line + '\n'

movie_info = ''
movie_stuff = ["movie_last_liked_name","movie_last_liked_genre"]
for e in embedded_variables:
    for m in movie_stuff:
        if e == "movie_last_liked_name":
            new_line = 'string ' + e + ' = GetComponenet<Controller>().user.movies[0].name;'
            movie_info = movie_info + new_line + '\n\t\t'
        if e == "movie_last_liked_genre":
            new_line = 'string ' + e + ' = GetComponenet<Controller>().user.movies[0].genre;'
            movie_info = movie_info + new_line + '\n\t\t'            
            

   
#add declarations...
declarations =  'string Avatar1NextText = "";\nstring Avatar2NextText = "";\n' + basic + '//avatar animation IDs....\n' + avatar_variables + '//scene variables...\n' + scene_variables  + '//booleans...\n' + booleans

generated = generated.replace('$','')

pre_str = 'using System.Collections;\nusing System.Collections.Generic;\nusing UnityEngine;\n\npublic class Dialogue : MonoBehaviour {\n\n    public Dialogue(){\n	}\n\n'	
GetNext = 'public void GetNext(){\n'


while_str = '\n\t\twhile( IsAvatarNode == false ) {\n'

post_str  = '\n}\n			List<string> dialogueOutput = new List<string> ();\n            //nextNode to be passed into GetNext()...\n			dialogueOutput.Add (nextNode);\n            //first Avatar animation calls...\n			dialogueOutput.Add (Avatar1NextText);\n			dialogueOutput.Add (Avatar1FaceModel);\n			dialogueOutput.Add (Avatar1FaceAnim);\n			dialogueOutput.Add (Avatar1BodyModel);\n			dialogueOutput.Add (Avatar1BodyAnim);\n			dialogueOutput.Add (Avatar1VoiceName);\n			dialogueOutput.Add (Avatar1VoiceEffects);\n            //second Avatar animation calls...\n			dialogueOutput.Add (Avatar2NextText);\n			dialogueOutput.Add (Avatar2FaceModel);\n			dialogueOutput.Add (Avatar2FaceAnim);\n			dialogueOutput.Add (Avatar2BodyModel);\n			dialogueOutput.Add (Avatar2BodyAnim);\n			dialogueOutput.Add (Avatar2VoiceName);\n			dialogueOutput.Add (Avatar2VoiceEffects);\n            //scene animation calls...\n			dialogueOutput.Add (SceneRendering);\n            dialogueOutput.Add (SceneLighting);\n			dialogueOutput.Add (SceneSound);\n			dialogueOutput.Add (NarratorSound);\n			dialogueOutput.Add (Screen);\n			return dialogueOutput;\n		}\n	}\n}\n'

updates = '\n//nextNode to be passed into GetNext()...\nGetComponent<Controller>().current_node = nextNode;\n//first Avatar animation calls...\nGetComponent<Controller>().Avatar1NextText      = Avatar1NextText;\nGetComponent<Controller>().Avatar1FaceModel     = Avatar1FaceModel;\nGetComponent<Controller>().Avatar1FaceAnim      = Avatar1FaceAnim;\nGetComponent<Controller>().Avatar1BodyModel     = Avatar1BodyModel;\nGetComponent<Controller>().Avatar1BodyAnim      = Avatar1BodyAnim;\nGetComponent<Controller>().Avatar1VoiceName     = Avatar1VoiceName;\nGetComponent<Controller>().Avatar1VoiceEffects  = Avatar1VoiceEffects;\n\nGetComponent<Controller>().Avatar2NextText      = Avatar2NextText;\nGetComponent<Controller>().Avatar2FaceModel     = Avatar2FaceModel;\nGetComponent<Controller>().Avatar2FaceAnim      = Avatar2FaceAnim;\nGetComponent<Controller>().Avatar2BodyModel     = Avatar2BodyModel;\nGetComponent<Controller>().Avatar2BodyAnim      = Avatar2BodyAnim;\nGetComponent<Controller>().Avatar2VoiceName     = Avatar2VoiceName;\nGetComponent<Controller>().Avatar2VoiceEffects  = Avatar2VoiceEffects;\n\n//scene animation calls...\nGetComponent<Controller>().SceneRendering       = SceneRendering;\nGetComponent<Controller>().SceneLighting        = SceneLighting;\nGetComponent<Controller>().SceneSound           = SceneSound;\nGetComponent<Controller>().NarratorSound        = NarratorSound;\nGetComponent<Controller>().Screen               = Screen;\n\n}\n}\n}'

similarity_str = '	public bool SimilarityCheck(List<string> toCompare){\n		//T0D0\n		//implement an actual semantic similarity checker\n		//currently this function compares string literals\n		string userSpeech = toCompare[0];\n		string toCheckAgainst;\n		int l = toCompare.Count;\n		int i = 1;\n		bool areSimilar = false;\n		while (i < l)\n		{\n			toCheckAgainst = toCompare [i];\n			if (userSpeech == toCheckAgainst){\n				areSimilar = true;\n			}\n			i++;\n		}\n		return areSimilar;\n	}\n\n\t'


g_lines = generated.split('\n')
generated = ''
for l in g_lines:
    l =  tab + tab + l
    generated = generated + l + '\n'

decs = declarations.split('\n')

declarations = tab + tab + 'string nextNode = "NONE";\n\t\tstring currentNode = GetComponent<Controller>().current_node;\n\t\tstring MicSpeech = GetComponent<Controller>().user.user_lines.Peek().toString();\n\t\tstring CamF = "";\n\t\t'



declarations = declarations + toAdd    

for d in decs:
    d = tab + tab  + d 
    if 'currentNode' not in d:
        declarations = declarations + d + '\n'
declarations = declarations + '\t\tList<string> toCompare = new List<string> ();\n'
parsed = pre_str + similarity_str + GetNext + declarations + while_str + generated + updates


outfile = open("generated.cs","w+")
outfile.write(parsed)
