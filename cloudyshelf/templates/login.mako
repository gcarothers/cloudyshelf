<html>
	<head>
		<title>Log-in</title>
	</head>
	<body>
		<form action="" method="POST">
			<p><label>E-Mail <input type="text" name="email" /></label></p>
			<p><label>Password <input type="text" name="password" /></label></p>
			<p><input type="submit" value="Log In" /> or <a href="${request.route_url('signup')}">Sign Up</a></p>
		</form>
	</body>
</html>
