FROM mongo:latest

# Copy the custom entrypoint script into the container
COPY travelDB-mongoDB/init-scripts/custom-entrypoint.sh /custom-entrypoint.sh
RUN chmod +x /custom-entrypoint.sh

# Use your custom entrypoint script
ENTRYPOINT ["/custom-entrypoint.sh"]
