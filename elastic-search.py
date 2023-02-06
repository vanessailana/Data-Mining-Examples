from elasticsearch import Elasticsearch
import pandas as pd 
#https://www.kaggle.com/datasets/jrobischon/wikipedia-movie-plots
es = Elasticsearch("http://localhost:9200")
es.info().body

#read the dataset 
df = (
    pd.read_csv("wiki_movie_plots_deduped.csv")
    .dropna()
    .sample(5000, random_state=42)
    .reset_index()
)
print(df.head(3))

#create the index 
mappings = {
        "properties": {
            "title": {"type": "text", "analyzer": "english"},
            "ethnicity": {"type": "text", "analyzer": "standard"},
            "director": {"type": "text", "analyzer": "standard"},
            "cast": {"type": "text", "analyzer": "standard"},
            "genre": {"type": "text", "analyzer": "standard"},
            "plot": {"type": "text", "analyzer": "english"},
            "year": {"type": "integer"},
            "wiki_page": {"type": "keyword"}
    }
}

es.indices.create(index="movies", mappings=mappings)



#add data to your index 
for i, row in df.iterrows():
    doc = {
        "title": row["Title"],
        "ethnicity": row["Origin/Ethnicity"],
        "director": row["Director"],
        "cast": row["Cast"],
        "genre": row["Genre"],
        "plot": row["Plot"],
        "year": row["Release Year"],
        "wiki_page": row["Wiki Page"]
    }
            
    es.index(index="movies", id=i, document=doc)

#check the number of documents indexed 
es.indices.refresh(index="movies")
es.cat.count(index="movies", format="json")

#make searches in your es index. 
resp = es.search(
    index="movies",
    query={
        "bool": {
            "must": {
                "match": {
                    "cast": "jack nicholson",
                }
            },
            "filter": {"bool": {"must_not": {"match_phrase": {"director": "roman polanksi"}}}},
        },
    },
)
print(resp)


#es.delete(index = "movies", id = "2500")
es.options(ignore_status=[400,404]).indices.delete(index='movies')