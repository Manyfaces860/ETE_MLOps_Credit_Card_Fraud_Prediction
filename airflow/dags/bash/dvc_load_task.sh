#!/bin/bash

# --- Script Arguments ---
# The first path to track with DVC (e.g., data/raw/raw_data.csv)
DVC_PATH1="$1"
# The second path to track with DVC (e.g., data/processed/processed_data.csv)
DVC_PATH2="$2"
# The Git commit message (e.g., "DVC: Versioned new raw and processed data")
GIT_COMMIT_MESSAGE="$3"


# --- Functions for logging ---
log_info() {
    echo "[INFO] $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_success() {
    echo "[SUCCESS] $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo "[ERROR] $(date '+%Y-%m-%d %H:%M:%S') - $1" >&2
    exit 1
}

# --- Argument Validation ---
# This script now expects at least 2 paths and an optional commit message.
# So, minimum 2 arguments (path1, path2). If 3rd is not provided, default commit message.
if [ "$#" -lt 2 ]; then
    log_error "Usage: $0 <path1_to_track> <path2_to_track> [commit_message]"
fi

# Set default commit message if not provided
if [ -z "$GIT_COMMIT_MESSAGE" ]; then
    GIT_COMMIT_MESSAGE="DVC: Versioned '$DVC_PATH1' and '$DVC_PATH2'"
    log_info "No custom commit message provided. Using default: '$GIT_COMMIT_MESSAGE'"
fi

# --- Script Start ---
log_info "Starting DVC configuration and data versioning script."
log_info "First path to track: '$DVC_PATH1'"
log_info "Second path to track: '$DVC_PATH2'"
log_info "Git commit message: '$GIT_COMMIT_MESSAGE'"

# 1. Ensure DVC is initialized in the current directory
if [ ! -d ".dvc" ]; then
    log_info "DVC not initialized (.dvc folder not found). Initializing DVC..."
    dvc init || log_error "Failed to initialize DVC."
    log_info "DVC initialized. Remember to commit .dvc/ to Git if this is the first time."
else
    log_info "DVC already initialized (.dvc folder found)."
fi

# 2. Check if the DVC remote is configured and set its region
log_info "Checking for DVC remote: $DVC_REMOTE_NAME..."
if dvc remote list | grep -q "$DVC_REMOTE_NAME"; then
    log_info "DVC remote '$DVC_REMOTE_NAME' is already configured."
else
    log_info "DVC remote '$DVC_REMOTE_NAME' not found. Configuring it now..."
    # Add the S3 remote. The -d flag sets it as the default remote.
    dvc remote add -d "$DVC_REMOTE_NAME" "$DVC_S3_BUCKET" || log_error "Failed to add DVC remote."
    log_success "DVC remote '$DVC_REMOTE_NAME' configured successfully."
fi


# 3. Add the specified paths to DVC tracking
log_info "Adding '$DVC_PATH1' and '$DVC_PATH2' to DVC tracking..."

# Ensure the first path exists before trying to add it
if [ ! -e "$DVC_PATH1" ]; then
    log_error "Error: Path '$DVC_PATH1' does not exist. Cannot add to DVC."
fi
# Ensure the second path exists before trying to add it
if [ ! -e "$DVC_PATH2" ]; then
    log_error "Error: Path '$DVC_PATH2' does not exist. Cannot add to DVC."
fi

# Add both paths in a single dvc add command
dvc add "$DVC_PATH1" "$DVC_PATH2" || log_error "Failed to run 'dvc add' on paths."
log_success "'$DVC_PATH1' and '$DVC_PATH2' added to DVC tracking."

# 5. Git add and commit changes
git add "$DVC_PATH2.dvc" || log_error "Failed to add '$DVC_PATH2.dvc' to Git."
git add "$DVC_PATH1.dvc" || log_error "Failed to add '$DVC_PATH1.dvc' to Git."
log_info "Committing changes to Git..."
git commit -m "$GIT_COMMIT_MESSAGE" || log_error "Failed to commit changes to Git. (Perhaps no changes?)"
log_success "Git changes committed successfully."

# 4. Push DVC-tracked data to the remote storage
log_info "Pushing DVC-tracked data to remote storage..."
dvc push $DVC_PATH1 $DVC_PATH2|| log_error "Failed to run 'dvc push'."
log_success "DVC-tracked data pushed to remote storage."

log_success "Script completed successfully!"
