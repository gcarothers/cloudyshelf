<html>
	<head>
		<title>My Bookshelf</title>
	</head>
	<body>
		<h1>Bookshelf For ${user.user_name}</h1>
		<ul>
		<%! import os.path %>
		%for f in files:
			<% book = os.path.basename(f['path']) %>
			<li><a href="${request.route_url('shelf_download', book=book)}"
			    >${book}</a></li>
		%endfor
		</ul>
	</body>
</html>