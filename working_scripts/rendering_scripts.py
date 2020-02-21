from django.core.paginator import Paginator


def get_pagination_info(request, posts, per_page=10):
    """
    request = HttpRequest object
    posts - posts needed for showing
    per_page - how many posts you want to show on one page
    return 'page' and 'paginator'
    """
    paginator = Paginator(posts, per_page)  # показывать по 10 записей на странице
    page_number = request.GET.get('page')  # переменная в url с номером запрошеной страницы
    page = paginator.get_page(page_number)  # получить записи с нужным смещением
    return page, paginator
