run-local:
	$(MAKE) -C backend start-backend &
	$(MAKE) -C frontend start-frontend &
	wait
	
