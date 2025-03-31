.PHONY: clean

clean:
	rm -rf *.pyc
	rm -rf **/*.pyc
	rm -rf **/**/*.pyc
	rm -rf **/**/**/*.pyc
	rm -rf **/**/**/**/*.pyc
	find . -type d -name "__pycache__" -exec rm -rf {} +