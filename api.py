from fastapi import FastAPI, Path
import recommend_ronan
import requests
import ast
import recommender_v2
app = FastAPI()

@app.get('/recommend')
def recommend_movie(keyword):
    df = recommend_ronan.recommend(keyword)
    return df

@app.get('/popular/{num_movies}')
def pop_movies(num_movies: int = Path(title="Number of Popular Movies")):
    df = recommend_ronan.pop_movies(num_movies)
    result = df['title'].to_list()
    return result
    
@app.get('/images/{tmdbId}')
def grab_poster(tmdbId: int = Path(title="tmdbId for the movie")):
    response = requests.get('https://api.themoviedb.org/3/movie/{}?api_key=621d3fee8614662e39e4cfea30a2a3ba&language=en-US'.format(tmdbId))
    data = response.content
    data = data.decode('UTF-8')
    data = data.replace('false','False')
    data = data.replace('null','""')
    data = ast.literal_eval(data)
    return 'https://image.tmdb.org/t/p/w500/{}'.format(data['poster_path'])

@app.get('/recommend2')
def recommend(input):
    data = recommender_v2.get_similar_movies(input)
    return data