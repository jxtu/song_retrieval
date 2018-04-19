from urllib import request

link = 'https://charts-static.billboard.com/img/2003/12/michael-jackson-9to-number-ones-f42-174x174.jpg'
a = request.urlretrieve(link, '111')
print(a)
print(244 * 110)