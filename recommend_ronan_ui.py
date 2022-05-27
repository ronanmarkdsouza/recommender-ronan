import streamlit as st
import ast
import requests
import pandas as pd
import pickle

movies = pd.read_csv('movies.csv')
links = pd.read_csv('links.csv')

def home():
    try:
        st.title("Home")
        st.write("Top Movies based on user rating")
        response = requests.get('http://127.0.0.1:8000/popular/12')
        data = ast.literal_eval(response.content.decode('UTF-8'))
        data = pd.DataFrame(data,columns=['title'])
        data = pd.merge(data,movies, on='title')
        data = pd.merge(data,links,on='movieId')
        display_movs(data)
    except:
        st.error("API not running!")

def search():
    st.title("Search for movie")
    # keyword = st.text_input(placeholder="Search", label='')
    movie_list = pickle.load(open('movie_list.pkl','rb'))
    input = st.selectbox("Enter Movie name",movie_list)
    option = st.radio("Recommendation Type",("Model-1","Model-2"))
    if st.button("Recommend"):
        if option=="Model-1":
            try:
                response = requests.get('http://127.0.0.1:8000/recommend?keyword={}'.format(input))
                data = ast.literal_eval(response.content.decode('UTF-8'))
                data = pd.DataFrame(data)
                data['movieId'] = data.index
                data['movieId'] = data['movieId'].astype('int64')
                data = pd.merge(data,links, on='movieId')
                data.drop(['genres','movieId','imdbId'],inplace=True,axis=1)
                display_movs(data)
            
            except:
                st.error("API not running!")
        
        elif option=="Model-2":
            try:
                response = requests.get('http://127.0.0.1:8000/recommend2?input={}'.format(input))
                temp = response.content.decode('UTF-8')
                data = ast.literal_eval(temp)
                data = pd.DataFrame(data,columns=['title'])
                data = pd.merge(data,movies, on='title')
                data = pd.merge(data,links,on='movieId')
                display_movs(data)
            except:
                st.error("API not running!")
        
          
def analytics():
    st.title("Analytics")
    st.write("This page is for model analytics")

def main():
    st.title("Movie Recommendation System")
    menu = ["Home", "Search","Analytics"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        home()

    elif choice == "Search":
        search()

    elif choice == "Analytics":
        analytics()

def display_movs(data):
    try:
        posters = []
        movie_names = []
        for key in range(len(data)):
            movie_names.append(data['title'][key])
            try:
                response = requests.get('http://127.0.0.1:8000/images/{}'.format(int(data['tmdbId'][key])))
                link = ast.literal_eval(response.content.decode('UTF-8'))
                posters.append(link)
            except:
                link = "Not found"
                posters.append(link)
                
        col1,col2,col3 = st.columns(3)
        col4,col5,col6 = st.columns(3)
        col7,col8,col9 = st.columns(3)
        col10,col11,col12 = st.columns(3)
        with col1:
            st.markdown(movie_names[0])
            st.image(posters[0])
        with col2:
            st.markdown(movie_names[1])
            st.image(posters[1])
        with col3:
            st.markdown(movie_names[2])
            st.image(posters[2])
        with col4:
            st.markdown(movie_names[3])
            st.image(posters[3])
        with col5:
            st.markdown(movie_names[4])
            st.image(posters[4])
        with col6:
            st.markdown(movie_names[5])
            st.image(posters[5])
        with col7:
            st.markdown(movie_names[6])
            st.image(posters[6])
        with col8:
            st.markdown(movie_names[7])
            st.image(posters[7])
        with col9:
            st.markdown(movie_names[8])
            st.image(posters[8])
        with col10:
            st.markdown(movie_names[9])
            st.image(posters[9])
        with col11:
            st.markdown(movie_names[10])
            st.image(posters[10])
        with col12:
            st.markdown(movie_names[11])
            st.image(posters[11])
    except:
        pass


if __name__ == "__main__":
    main()