<html>
	<head>
		<title>My Bookshelf</title>
	</head>
	<body>
		<h1>Bookshelf For ${user.user_name}</h1>
		<ul>
		%for f in files:
			<li>${f['path']}</li>
		%endfor
		</ul>
	</body>
</html>