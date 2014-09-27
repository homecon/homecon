<?php
echo "
		<article class=$page_class>";
		
include("clock.php");
	
echo "
			<hr>
";	
	
include("lokaal_weer.php");

echo "
			<hr>
";	
	
include("weerbericht.php");

echo "		<hr>
		</article>	
";
?>