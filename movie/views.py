from collections import defaultdict
from django.shortcuts import render
from django.http import HttpResponse

from .models import Movie

import matplotlib.pyplot as plt
import matplotlib
import io
import urllib, base64

# Create your views here.
def home(request):
    #return HttpResponse('<h1>Welcome to Home Page</h1>')
    #return render(request, 'home.html', {'name': 'Marcela Londoño'})
    searchTerm = request.GET.get('searchMovie')
    if searchTerm:
        movies = Movie.objects.filter(title__icontains=searchTerm)
    else:
        movies = Movie.objects.all()
    return render(request, 'home.html', {'searchTerm': searchTerm, 'movies': movies})

def about(request):
    #return HttpResponse('<h1>Welcome to About Page</h1>')
    return render(request, 'about.html')

def signup(request):
    email = request.GET.get('email')
    return render(request, 'signup.html', {'email': email})

def statistics_view(request):
    matplotlib.use('Agg')
    #Gráfica por años
    years = Movie.objects.values_list('year', flat=True).distinct().order_by('year') #Obtener todos los años de las películas
    movie_counts_by_year = {} #Crear un diccionario para almacenar la cantidad de películas por años
    for year in years: #Contar la cantidad de películas por año
        if year:
            movies_in_year = Movie.objects.filter(year=year)
        else:
            movies_in_year = Movie.objects.filter(year__isnull=True)
            year = "None"
        count = movies_in_year.count()
        movie_counts_by_year[year] = count
    bar_width = 0.5 #Ancho de las barras
    bar_spacing = 0.5 #Separación de las barras
    bar_positions_year = range(len(movie_counts_by_year)) #Posiciones de las barras
    
    #Crear la gráfica de barras
    plt.bar(bar_positions_year, movie_counts_by_year.values(), width=bar_width, align='center')
    #Personalizar la gráfica
    plt.title('Movies per year')
    plt.xlabel('Year')
    plt.ylabel('Number of movies')
    plt.xticks(bar_positions_year, movie_counts_by_year.keys(), rotation=90)
    #Ajustar el espaciado entre las barras
    plt.subplots_adjust(bottom=0.3)
    #Guardar la gráfica en un objeto BytesIO
    buffer_year = io.BytesIO()
    plt.savefig(buffer_year, format='png')
    buffer_year.seek(0)
    plt.close()
    
    #Convertir la gráfica a base64
    image_png_year = buffer_year.getvalue()
    buffer_year.close()
    graphic_year = base64.b64encode(image_png_year)
    graphic_year = graphic_year.decode('utf-8')
    
    #Gráfica por géneros
    movies = Movie.objects.all()
    movies_counts_by_genre = defaultdict(int)
    for movie in movies:
        if movie.genre:
            first_genre = movie.genre.split(',')[0]
            first_genre = first_genre.strip()
            if first_genre:
                movies_counts_by_genre[first_genre] += 1
    bar_positions_genre = range(len(movies_counts_by_genre))
    plt.bar(bar_positions_genre, movies_counts_by_genre.values(), width=bar_width, align='center')
    plt.title('Movies per Genre')
    plt.xlabel('Genre')
    plt.ylabel('Number of movies')
    plt.xticks(bar_positions_genre, movies_counts_by_genre.keys(), rotation=90)
    plt.subplots_adjust(bottom=0.3)
    
    buffer_genre = io.BytesIO()
    plt.savefig(buffer_genre, format='png')
    buffer_genre.seek(0)
    plt.close()
    
    image_png_genre = buffer_genre.getvalue()
    buffer_genre.close()
    graphic_genre = base64.b64encode(image_png_genre).decode('utf-8')
    #Renderizar la plantilla statistics.html con la gráfica
    return render(request, 'statistics.html', {'graphic_year': graphic_year, 'graphic_genre': graphic_genre})