from django.shortcuts import render, redirect
from django.http import HttpResponse
from article_manager.models import Article
from article_manager.forms import ArticleForm

from article_manager.libre import LibreManager

from django.conf import settings

from difflib import Differ

# Create your views here.
def articles_list(request):
    stored_articles = Article.objects.all()
    remote = LibreManager(settings.DOKUWIKI_USERNAME, settings.DOKUWIKI_PASSWORD)
    
    links = remote.getLocalLinks("wiki:prikupljeni_clanci") # get all available links from dokuwiki
    
    not_updated = [] # This is list for placing articles which have not been imported yet
    for link in links:
        if not Article.slugInDatabase(link):
            not_updated.append(link)
    context = { 'dokuwiki_articles' : not_updated,
                'stored_articles' : stored_articles,
                }
    return render(request, 'articles_list.html', context)

def article_view(request, article_id):
    article = Article.objects.get(pk=int(article_id))
    context = {"article": article}
    return render(request, "article_view.html", context)

def article_diff(request, article_id):
    article = Article.objects.get(pk= int(article_id))
    diff = [] 
    remote = LibreManager(settings.DOKUWIKI_USERNAME, settings.DOKUWIKI_PASSWORD)
    wiki_article = remote.getPage(article.source_lat)
    t1 = []
    t2 = []
    if wiki_article.isCyr():
        t1 = article.contents_cyr.split("\n")
        t2 = wiki_article.getText().split("\n")
    else:
        t1 = article.contents_lat.split("\n")
        t2 = wiki_article.getText().split("\n")
    # We remove blank lines 
    nt1 = [] 
    nt2 = [] 
    for line in t1: 
        if line.strip() != "":
            nt1.append(line.replace("\r", ""))
    for line in t2:
        if line.strip() != "":
            nt2.append(line.replace("\r", ""))
    d = Differ()
    diff = list(d.compare(nt1, nt2))
    context = {"diff": diff}
    return render(request, "article_diff.html", context)

def wiki_import(request, wiki_slug, script):
    if request.method == "GET":
        entry = Article.fromRemote(wiki_slug)
        entry.save()
        return redirect("article_submit", entry.pk, script)
