import pandas as pd
import numpy as np
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
from sklearn.preprocessing import OrdinalEncoder
import re

links =  pd.read_csv('links.csv')
movies = pd.read_csv('movies.csv')
ratings = pd.read_csv('ratings.csv')
tags = pd.read_csv('tags.csv')

ratings.drop('timestamp', inplace=True, axis=1)
tags.drop('timestamp', inplace=True, axis=1)

mov_rat = pd.merge(movies, ratings)

mov_rat['genres'] = mov_rat.apply(lambda x: x['genres'].split('|'),axis=1)

mlb = MultiLabelBinarizer()
trans  = mlb.fit_transform(mov_rat['genres'])
label = pd.DataFrame(data=trans, columns=mlb.classes_)
data = pd.concat([mov_rat, label], axis=1)
data_gb = data.groupby(['userId','title'])
data = data_gb.first()

data.drop(columns=['genres','(no genres listed)','IMAX'], inplace=True)

user_mat = pd.pivot_table(data=data, index=['userId'],aggfunc=np.sum)
user_mat = user_mat.drop(columns=['rating','movieId'])
cos_mat = pd.DataFrame(cosine_similarity(user_mat,user_mat), columns=np.arange(1,611,1)).set_index(np.arange(1,611,1))

mean_rat = ratings.groupby('movieId').rating.mean()
num_users = ratings.groupby('movieId').userId.count()
mean_rat_movie_temp = pd.merge(mean_rat, movies, how='inner', on='movieId')
mean_rat_movie = pd.merge(mean_rat_movie_temp, num_users, how='inner', on='movieId')
mean_rat_movie.drop(columns='genres', inplace=True)
mean_rat_movie.rename(columns={'rating':'mean_ratings','userId':'num_users'}, inplace=True)

pop_movs = mean_rat_movie[mean_rat_movie["num_users"]>110].sort_values('mean_ratings',ascending=False)

df = pd.merge(movies, tags, on='movieId')
df = pd.merge(df, ratings, on=['userId','movieId'])
df['genres'] = df.apply(lambda x: x['genres'].split('|'),axis=1)

def extract_year(inp_str):
    year = re.findall(r'\(.*?\)', inp_str)
    for i in year:
        temp = str(i).replace(')','')
        year = temp.replace('(','')
    return year

df['year'] = df['title'].apply(lambda x: extract_year(x))

def encode(series, encoder):
    return encoder.fit_transform(series.values.reshape((-1, 1))).astype(int).reshape(-1)
user_encoder, movie_encoder = OrdinalEncoder(), OrdinalEncoder()
df['user_id_encoding'] = encode(df.userId, user_encoder)
df['movie_id_encoding'] = encode(df.movieId, movie_encoder)
X = csr_matrix((df.rating, (df.user_id_encoding, df.movie_id_encoding)))

V = cosine_similarity(X.T, X.T)

movie_encoder.inverse_transform([[1]])

offline_results = {
    movie_id: np.argsort(similarities)[::-1]
    for movie_id, similarities in enumerate(V)
}

def get_recommendations(movie_title, top_n):
    movie_id = movies.set_index('title').loc[movie_title][0]
    movie_csr_id = movie_encoder.transform([[movie_id]])[0, 0].astype(int)
    rankings = offline_results[movie_csr_id][:top_n]
    ranked_indices = movie_encoder.inverse_transform(rankings.reshape((-1, 1))).reshape(-1)
    return movies.set_index('movieId').loc[ranked_indices]

def recommend(keyword):
    if len(return_mov(keyword)) >0:
        return get_recommendations(return_mov(keyword)[0],6)
    else:
        print("No recommended movies")

def cor_char(list):
    for i in range(len(list)):
        list[i] = list[i].lower().strip(":;,.''[]}{)(*&^%$#@!|")
    return list

def return_mov(keyword):
    movie_names = []
    name_token = keyword.split(' ')
    for i in range(search_df.shape[0]):
        for j in range(len(name_token)):
            if name_token[j].lower().strip(":;,.''[]}{)(*&^%$#@!|") in search_df.loc[i,"keywords"]:
                movie_names.append(search_df.loc[i,"title"])
    result = list(dict.fromkeys(movie_names))
    return result

def pop_movies(number_of_movies):
    df = pop_movs.head(number_of_movies)
    return df

search_df = pd.DataFrame()
search_df['title'] = df['title']
search_df['movieId'] = df['movieId']
search_df['genres'] = df['genres']
search_df['keywords'] = df.apply(lambda x: [x['tag'],x['year']], axis=1)
search_df.apply(lambda x: x['keywords'].extend(x['title'].split(' ')),axis=1)
search_df.apply(lambda x: x['keywords'].extend(x['genres']),axis=1)
search_df.drop('genres',inplace=True,axis=1)
for i in search_df['keywords']:
    try:
        i = cor_char(i)
    except:
        pass
search_df