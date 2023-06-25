### setup
import random
import pyttsx3

import openai
openai.api_key = "OPENAI-API-KEY"
openai_client = openai.Completion

import anthropic
anthropic_client = anthropic.Client("ANTHROPIC-API-KEY")

### parameters
debate_topic = input("What topic would you like to hear about?\n\n")
debaters = ["Open AI", "Anthropic"]
rounds = 8
openai_model = "text-davinci-003"
anthropic_model = "claude-v1"
openai_moderator_model = "text-davinci-002"
ttt_file_name = "ai_debate_transcription.txt"
tts_file_name = 'ai_debate_audio.mp3'
should_include_moderator = True
should_perform_text_to_speech = False

### debate simulation
debater_responses = ["Pretend you are a debater. What are your thoughts on " + debate_topic + "?"]
responses_to_print = []
for i in range(rounds):
  debater = debaters[0] if i % 2 == 0 else debaters[1]
  
  if should_include_moderator:
    # using another openAI model to generate a debate prompt
    moderator_prompt = "Pretend you are a debate moderator. The original topic is " + debate_topic + ". The latest response was " + debater_responses[-1] + "Rather than providing your own response, give me a question me how to respond to that by randomly choosing to agree or disagree."
    moderator_response = openai_client.create(engine=openai_moderator_model, prompt=moderator_prompt, max_tokens=100)
    debater_prompt = moderator_response.choices[0].text
    moderator_response_to_print = "Moderator: " + debater_prompt + "\n\n"
    responses_to_print.append(moderator_response_to_print)
    print(moderator_response_to_print)
  else:
    agree_or_disagree = "agree to " if random.randint(0, 1) == 0 else "argue against"
    debater_prompt = "The original topic is " + debate_topic + ". In 250 characters or less, how would you " + agree_or_disagree + " to the following response: " + debater_responses[-1] + " You don't need to say explicitly if you agree or disagree. You must use full sentences."

  if i % 2 == 0: # openai's turn
    api_response = openai_client.create(engine=openai_model, prompt=debater_prompt, max_tokens=100)
    debater_response_text = api_response.choices[0].text
  else: # anthropic's turn
    api_response = anthropic_client.completion(
      prompt=f"{anthropic.HUMAN_PROMPT} {debater_prompt} {anthropic.AI_PROMPT}",
      model=anthropic_model,
      max_tokens_to_sample=100,
    )
    debater_response_text = api_response['completion']
    # post-process anthropic's response text
    debater_response_text = '.'.join(list(filter(lambda c: "Here is" not in c and "250" not in c, debater_response_text.split('.'))))

  debater_responses.append(debater_response_text)
  debater_response_to_print = debater + ": " + debater_response_text + "\n\n"
  responses_to_print.append(debater_response_to_print)
  print(debater_response_to_print)

### TTT
output_file = open(ttt_file_name, "w")
for response_to_print in responses_to_print:
  output_file.write(response_to_print)
output_file.close()

### TTS
if should_perform_text_to_speech:
  debater_responses.pop(0) # get rid of initial prompt
  engine = pyttsx3.init()
  for debater_response in debater_responses:
    engine.say(debater_response)
  engine.runAndWait()
