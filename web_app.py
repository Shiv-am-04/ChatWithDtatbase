import streamlit as st
import os
from PIL import Image
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from pathlib import Path
from langchain_community.utilities import SQLDatabase
from langchain.agents.agent_types import AgentType
from langchain.agents import create_sql_agent
from langchain.callbacks import StreamlitCallbackHandler
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from sqlalchemy import create_engine
import sqlite3

load_dotenv()

groq_api_key = os.getenv('GROQ_API_KEY')

llm = ChatGroq(model='Gemma2-9b-It',groq_api_key=groq_api_key)

img = Image.open('database.png')

st.set_page_config(page_title='DataBase Homie',page_icon='database.png')

col1,col2 = st.columns([1,3])

with col1:
    st.image(img,use_column_width=True)

with col2:
    st.title('Fetch from DataBase')

LOCALDB = 'USE_LOCALDB'
SQL = 'USE_POSTGRESQL'


# st.cache_resource is a decorator used to cache the results of resource-heavy operations to speed up your app. 
# By caching, you avoid re-running the same code multiple times. The ttl parameter in st.cache_resource stands for 
# "time-to-live." It specifies how long,a cached resource should be retained before it is re-evaluated.
@st.cache_resource(ttl='1h')
def configure_database(database_uri,host=None,user_name=None,password=None,database=None):
    if database_uri == LOCALDB:
        # __path__ is a special variable that typically refers to the current module’s directory. 
        # Path(__path__).parent gets the parent directory of this path.
        # .absolute() Converts the resulting path to an absolute path, ensuring it is a full path from the root of the filesystem.
        db_file_path = (Path(__file__).parent/'studentDB.db').absolute()

        # This lambda function, when called, will establish a connection to the SQLite database located at the db_file_path.
        # mode=ro sets the connection to read-only mode.
        # uri=True tells SQLite to interpret the database path as a URI.
        creator = lambda : sqlite3.connect(f"file:{db_file_path}?mode=ro",uri=True)

        return SQLDatabase(create_engine('sqlite:///',creator=creator))

    elif database_uri == 'USE_MYSQL':
        if not (database_uri and host and user_name and password and database):
            st.info("Please provide the connection details")
        else:
            return SQLDatabase(create_engine(f'mysql+mysqlconnector://{user_name}:{password}@{host}/{database}'))
        
    else:
        if not(database_uri and host and user_name and password and database):
            st.info("Please provide the connection details")
        else:    
            return SQLDatabase(create_engine(f'postgresql+psycopg2://{user_name}:{password}@{host}/{database}'))      

def toolkit_AND_action(DB,llm):
    # SQLDatabaseToolkit is for interacting with SQL databases using llm.
    toolkit = SQLDatabaseToolkit(db=DB,llm=llm)
    # creating agent
    agent = create_sql_agent(llm=llm,
                toolkit=toolkit,
                agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                verbose=True)
    
    return agent

radio_option = ['Use Student DataBase','Use your own DataBase']

selected_option = st.sidebar.radio('Choose DataBase you want to use',options=radio_option)

if radio_option.index(selected_option) == 1:
    # A Uniform Resource Identifier (URI) is a unique sequence of characters that identifies 
    # an abstract or physical resource on the internet.
    sql = st.sidebar.text_input(label='RDBMS',placeholder='MySQL')
    if sql in ['PostgreSQl','postgreSQL','postgresql','Postgresql']:
        database_uri = SQL
        host = st.sidebar.text_input(label='host',placeholder='localhost:0000')
        user_name = st.sidebar.text_input(label='user name')
        password = st.sidebar.text_input(label='password',type='password')
        database = st.sidebar.text_input(label='DataBase',placeholder='name of database')
        if host and user_name and password and database:
            DB = configure_database(database_uri,host,user_name,password,database)
            agent = toolkit_AND_action(DB,llm)
        else:
            st.warning('complete your details to configure database')
    elif sql in ['MySQl','mySQL','mysql']:
        database_uri = 'USE_MYSQL'
        host = st.sidebar.text_input(label='host',placeholder='localhost:0000')
        user_name = st.sidebar.text_input(label='user name')
        password = st.sidebar.text_input(label='password',type='password')
        database = st.sidebar.text_input(label='DataBase',placeholder='name of database')
        DB = configure_database(database_uri,host,user_name,password,database)
        if host and user_name and password and database:
            DB = configure_database(database_uri,host,user_name,password,database)
            agent = toolkit_AND_action(DB,llm)
        else:
            st.warning('complete your details to configure database')
    else:
        st.warning('Provide Your RDBMS')

else:
    database_uri = LOCALDB
    DB = configure_database(database_uri)
    agent = toolkit_AND_action(DB,llm)
    
# if not database_uri:
#     st.info('Please select default DataBase or connect with your own DataBase')


#### creating chat interface ####

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {'role':'ai','content':'ask for SQL query'}
    ]

for message in st.session_state.messages:
    st.chat_message(message['role']).write(message['content'])


prompt = st.chat_input(placeholder='ask for SQL query')

if prompt:
    st.session_state.messages.append({'role':'user','content':prompt})
    st.chat_message('human').write(prompt)

    with st.chat_message('ai'):
        callback = StreamlitCallbackHandler(st.container(),expand_new_thoughts=True)
        response = agent.run(st.session_state.messages,callbacks=[callback])
        st.session_state.messages.append({'role':'ai','content':response})
        st.write(response)

