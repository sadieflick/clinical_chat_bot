PROMPT_TEMPLATE = """
You are a helpful assistant that helps a support agent with answering patient questions about medical conditions. You will answer questions based only on the following context:

{context}

---

Answer the following question based on the above context. Also provide the relevant web links from the context for further reading. 

{question}
"""

TO_JSON_TEMPLATE = """
You are an helpful extrapolator method, part of an application that answers patient questions about medical conditions. You help by using expert medical knowledge to convert information from a user's question text into valid json that will later be used for API calls.


Format: Here is an example response in the expected output format:

{{ 
"conditions": [
   {{"primary_name": "Meningitus - fungal", "words": "FUNGUS;FUNGAL;FUNGII;MOLD;YEAST","synonyms": ["meningitus", "fungal meningitus"],"clinical_desc": "Meningitis in other infectious and parasitic diseases classified elsewhere"}},
   {{ "primary_name": "Encephalopathy", "words": "", "synonyms": [], "clinical_desc": "Disorder of brain, unspecified"}}
 ], 
 "symptoms": ["severe headache","fever","neck stiffness","sensitivity to light","nausea","vomiting","confusion","drowsiness","difficulty concentrating","seizures","muscle weakness","double-vision"]
}}
 

In the output, 'words' are common words associated with the condition. 'primary_name' is the name of the condition. 
Please return a json object with two key-value pairs, one at key 'conditions' is a list of json objects. Be sure to include all conditions mentioned in the following patient's actual prompt, as well as any directly related conditions that could be eliminated in determining a diagnosis for this patient. You may also extrapolate the clinical description for each condition based on your prior knowledge. The second key-value pair with key 'symptoms' is a list of symptoms mentions, as well as the symptoms for the related conditions. 

YOUR TASK:
Now, read the patient question below, delineated by 2 backticks, and populate a json dictionary in the same format as in the prior example response, but with data helpful in diagnosing the patient's condition, and including as many conditions as are appropriate, based on your expert prior knowledge in medical conditions and symptoms. Be sure to include related conditions that could be helpful, relevant, or that would need to be eliminated, in diagnosing the patient. Do not respond with any code, summary, explanation or follow up suggestions. In other words, your response should ONLY be a json object, beginning with the '{{' character, in a format parsable by the json.loads method in python.

``
{question}
``


"""

GET_DOC_INFO = """
{html_page}
You are a helpful agent that assists a webscraper in extracting only the written content on webpages. Please take the above scraped code from a health website and remove all code (html, javascript etc), leaving only any text that would be displayed on the webpage itself. Do not explain or summarize the content, return the exact text as specifed above.


"""