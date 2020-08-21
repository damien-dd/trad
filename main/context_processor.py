from .forms import SearchForm

def form_search(request):
	return {'form_search': SearchForm(initial={'done': True})}

