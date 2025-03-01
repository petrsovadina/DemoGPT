# Building an application

# Now we can start building our language model application. LangChain provides many modules that can be used to build language model applications. Modules can be used as stand-alones in simple applications and they can be combined for more complex use cases.

# LLMs
# Get predictions from a language model
# The basic building block of LangChain is the LLM, which takes in text and generates more text.

# As an example, suppose we're building an application that generates a company name based on a company description. In order to do this, we need to initialize an OpenAI model wrapper. In this case, since we want the outputs to be MORE random, we'll initialize our model with a HIGH temperature.

from langchain.llms import OpenAI

llm = OpenAI(temperature=0.9)

# And now we can pass in text and get predictions!

llm.predict(
    "What would be a good company name for a company that makes colorful socks?"
)
# >> Feetful of Fun

# Chat models
# Chat models are a variation on language models. While chat models use language models under the hood, the interface they expose is a bit different: rather than expose a "text in, text out" API, they expose an interface where "chat messages" are the inputs and outputs.

# You can get chat completions by passing one or more messages to the chat model. The response will be a message. The types of messages currently supported in LangChain are AIMessage, HumanMessage, SystemMessage, and ChatMessage -- ChatMessage takes in an arbitrary role parameter. Most of the time, you'll just be dealing with HumanMessage, AIMessage, and SystemMessage.

from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage

chat = ChatOpenAI(temperature=0)
chat.predict_messages(
    [
        HumanMessage(
            content="Translate this sentence from English to French. I love programming."
        )
    ]
)
# >> AIMessage(content="J'aime programmer.", additional_kwargs={})


# It is useful to understand how chat models are different from a normal LLM, but it can often be handy to just be able to treat them the same. LangChain makes that easy by also exposing an interface through which you can interact with a chat model as you would a normal LLM. You can access this through the predict interface.

chat.predict("Translate this sentence from English to French. I love programming.")
# >> J'aime programmer

# Prompt templates
# Most LLM applications do not pass user input directly into an LLM. Usually they will add the user input to a larger piece of text, called a prompt template, that provides additional context on the specific task at hand.

# In the previous example, the text we passed to the model contained instructions to generate a company name. For our application, it'd be great if the user only had to provide the description of a company/product, without having to worry about giving the model instructions.

# LLMs
# Chat models
# With PromptTemplates this is easy! In this case our template would be very simple:

from langchain.prompts import PromptTemplate

prompt = PromptTemplate.from_template(
    "What is a good name for a company that makes {product}?"
)
prompt.format(product="colorful socks")

# What is a good name for a company that makes colorful socks?

# Similar to LLMs, you can make use of templating by using a MessagePromptTemplate. You can build a ChatPromptTemplate from one or more MessagePromptTemplates. You can use ChatPromptTemplate's format_messages method to generate the formatted messages.

# Because this is generating a list of messages, it is slightly more complex than the normal prompt template which is generating only a string. Please see the detailed guides on prompts to understand more options available to you here.

from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

template = (
    "You are a helpful assistant that translates {input_language} to {output_language}."
)
system_message_prompt = SystemMessagePromptTemplate.from_template(template)
human_template = "{text}"
human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

chat_prompt = ChatPromptTemplate.from_messages(
    [system_message_prompt, human_message_prompt]
)

chat_prompt.format_messages(
    input_language="English", output_language="French", text="I love programming."
)


[
    SystemMessage(
        content="You are a helpful assistant that translates English to French.",
        additional_kwargs={},
    ),
    HumanMessage(content="I love programming."),
]

# Chains
# Now that we've got a model and a prompt template, we'll want to combine the two. Chains give us a way to link (or chain) together multiple primitives, like models, prompts, and other chains.

# LLMs
# Chat models
# The simplest and most common type of chain is an LLMChain, which passes an input first to a PromptTemplate and then to an LLM. We can construct an LLM chain from our existing model and prompt template.

# Using this we can replace

# llm.predict("What would be a good company name for a company that makes colorful socks?")

# with

from langchain.chains import LLMChain

chain = LLMChain(llm=llm, prompt=prompt)
chain.run("colorful socks")

# Feetful of Fun

# The LLMChain can be used with chat models as well:

from langchain import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

chat = ChatOpenAI(temperature=0)

template = (
    "You are a helpful assistant that translates {input_language} to {output_language}."
)
system_message_prompt = SystemMessagePromptTemplate.from_template(template)
human_template = "{text}"
human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
chat_prompt = ChatPromptTemplate.from_messages(
    [system_message_prompt, human_message_prompt]
)

chain = LLMChain(llm=chat, prompt=chat_prompt)
chain.run(
    input_language="English", output_language="French", text="I love programming."
)

# J'aime programmer.

# Memory
# The chains and agents we've looked at so far have been stateless, but for many applications it's necessary to reference past interactions. This is clearly the case with a chatbot for example, where you want it to understand new messages in the context of past messages.

# The Memory module gives you a way to maintain application state. The base Memory interface is simple: it lets you update state given the latest run inputs and outputs and it lets you modify (or contextualize) the next input using the stored state.

# There are a number of built-in memory systems. The simplest of these is a buffer memory which just prepends the last few inputs/outputs to the current input - we will use this in the example below.

# LLMs
# Chat models
from langchain import ConversationChain, OpenAI

llm = OpenAI(temperature=0)
conversation = ConversationChain(llm=llm, verbose=True)

conversation.run("Hi there!")

# here's what's going on under the hood

# > Entering new chain...
# Prompt after formatting:
# The following is a friendly conversation between a human and an AI. The AI is talkative and provides lots of specific details from its context. If the AI does not know the answer to a question, it truthfully says it does not know.

# Current conversation:

# Human: Hi there!
# AI:

# > Finished chain.

# >> 'Hello! How are you today?'

# You can use Memory with chains and agents initialized with chat models. The main difference between this and Memory for LLMs is that rather than trying to condense all previous messages into a string, we can keep them as their own unique memory object.

from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)

prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(
            "The following is a friendly conversation between a human and an AI. The AI is talkative and "
            "provides lots of specific details from its context. If the AI does not know the answer to a "
            "question, it truthfully says it does not know."
        ),
        MessagesPlaceholder(variable_name="history"),
        HumanMessagePromptTemplate.from_template("{input}"),
    ]
)

llm = ChatOpenAI(temperature=0)
memory = ConversationBufferMemory(return_messages=True)
conversation = ConversationChain(memory=memory, prompt=prompt, llm=llm)

conversation.predict(input="Hi there!")


# Hello! How can I assist you today?

conversation.predict(input="I'm doing well! Just having a conversation with an AI.")

# That sounds like fun! I'm happy to chat with you. Is there anything specific you'd like to talk about?


conversation.predict(input="Tell me about yourself.")

# Sure! I am an AI language model created by OpenAI. I was trained on a large dataset of text from the internet, which allows me to understand and generate human-like language. I can answer questions, provide information, and even have conversations like this one. Is there anything else you'd like to know about me?
