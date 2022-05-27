import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
df_movies = pd.read_csv("movies.csv")
df_ratings=pd.read_csv("ratings.csv")
df = pd.merge(df_movies,df_ratings,on='movieId')
moviemat2 = df.pivot_table(index='title',columns='userId',values='rating').fillna(0)
movie_to_user_sparse_df = csr_matrix(moviemat2.values)
movies_list = list(moviemat2.index)
knn_movie_model = NearestNeighbors(metric='cosine', algorithm='brute')
knn_movie_model.fit(movie_to_user_sparse_df)
movie_dict = {movie : index for index, movie in enumerate(movies_list)}
def get_similar_movies(movie, n = 12):
  index = movie_dict[movie]
  knn_input = np.asarray([moviemat2.values[index]])
  n = min(len(movies_list)-1,n)
  distances, indices = knn_movie_model.kneighbors(knn_input, n_neighbors=n+1)
  recommended = []
  for i in range(1,len(distances[0])):
    recommended.append(movies_list[indices[0][i]])
  return recommended