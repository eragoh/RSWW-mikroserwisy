FROM mongo:4.4.9

# Copy the custom entrypoint script into the container
COPY init-scripts/custom-entrypoint.sh /custom-entrypoint.sh
RUN chmod +x /custom-entrypoint.sh

# Use your custom entrypoint script
ENTRYPOINT ["/custom-entrypoint.sh"]
