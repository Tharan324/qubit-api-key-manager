# Use an official lightweight Python image
FROM python:3.10

# Set the working directory inside the container
WORKDIR /qubit-api-key-manager

# Copy only requirements first for caching
COPY requirements.txt requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . /qubit-api-key-manager

# Set environment variables
ENV PYTHONPATH=/qubit-api-key-manager/src

# Expose the port Flask/Gunicorn runs on
EXPOSE 8080

# Run Gunicorn with your wsgi.py file
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "wsgi:app"]