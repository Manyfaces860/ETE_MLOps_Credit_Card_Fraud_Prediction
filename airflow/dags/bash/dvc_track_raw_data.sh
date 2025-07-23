#!/bin/bash

# --- Configuration ---
DVC_REMOTE_NAME="$DVC_REMOTE_NAME"
DVC_S3_BUCKET="$DVC_S3_BUCKET" # IMPORTANT: Replace with your S3 bucket path

# --- Script Arguments ---
# The path to track with DVC (e.g., data/processed/model_input_features.csv)
DVC_PATH_TO_TRACK="$1"
# The Git commit message (e.g., "DVC: Versioned new features")
GIT_COMMIT_MESSAGE="$2"



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
if [ -z "$DVC_PATH_TO_TRACK" ]; then
    log_error "Usage: $0 <path_to_track> [commit_message]"
fi

if [ -z "$GIT_COMMIT_MESSAGE" ]; then
    GIT_COMMIT_MESSAGE="DVC: Versioned $DVC_PATH_TO_TRACK"
    log_info "No custom commit message provided. Using default: '$GIT_COMMIT_MESSAGE'"
fi

# --- Script Start ---
log_info "Starting DVC configuration and data versioning script."
log_info "Path to track: '$DVC_PATH_TO_TRACK'"
log_info "Git commit message: '$GIT_COMMIT_MESSAGE'"

# 1. Ensure DVC is initialized in the current directory
if [ ! -d ".dvc" ]; then
    log_info "DVC not initialized. Initializing DVC..."
    dvc init || log_error "Failed to initialize DVC."
    log_info "DVC initialized. Remember to commit .dvc/ to Git if this is the first time."
else
    log_info "DVC already initialized."
fi

# 2. Check if the DVC remote is configured
log_info "Checking for DVC remote: $DVC_REMOTE_NAME..."
if dvc remote list | grep -q "$DVC_REMOTE_NAME"; then
    log_info "DVC remote '$DVC_REMOTE_NAME' is already configured."
else
    log_info "DVC remote '$DVC_REMOTE_NAME' not found. Configuring it now..."
    # Add the S3 remote. The -d flag sets it as the default remote.
    dvc remote add -d "$DVC_REMOTE_NAME" "$DVC_S3_BUCKET" || log_error "Failed to add DVC remote."
    log_success "DVC remote '$DVC_REMOTE_NAME' configured successfully."
fi

# 3. Add the specified path to DVC tracking
log_info "Adding '$DVC_PATH_TO_TRACK' to DVC tracking..."
# Ensure the file/directory exists before trying to add it
if [ ! -e "$DVC_PATH_TO_TRACK" ]; then
    log_error "Error: Path '$DVC_PATH_TO_TRACK' does not exist. Cannot add to DVC."
fi
dvc add "$DVC_PATH_TO_TRACK" || log_error "Failed to run 'dvc add' on '$DVC_PATH_TO_TRACK'."
log_success "'$DVC_PATH_TO_TRACK' added to DVC tracking."

# 4. Push DVC-tracked data to the remote storage
log_info "Pushing DVC-tracked data to remote storage..."
dvc push || log_error "Failed to run 'dvc push'."
log_success "DVC-tracked data pushed to remote storage."

# 5. Git add and commit changes
log_info "Adding .dvc files and dvc.lock to Git..."
# Use -A to add all changes, including newly created .dvc files and updated dvc.lock
git add "$DVC_PATH_TO_TRACK.dvc" || log_error "Failed to add .dvc file to Git."
# Check if dvc.lock exists before adding it (it's created after dvc repro or dvc add on a pipeline)
if [ -f "dvc.lock" ]; then
    git add "dvc.lock" || log_error "Failed to add dvc.lock to Git."
fi
log_info "Committing changes to Git..."
git commit -m "$GIT_COMMIT_MESSAGE" || log_error "Failed to commit changes to Git. (Perhaps no changes?)"
log_success "Git changes committed successfully."

log_success "Script completed successfully!"
