# CORS Development Setup

This document explains how to configure CORS (Cross-Origin Resource Sharing) for local development with multiple frontend ports.

## Current Configuration

The development environment is configured to allow CORS requests from the following origins:

### CORS Allowed Origins

- `http://localhost:3000` (default frontend port)
- `http://localhost:3001` (alternative frontend instance)
- `http://localhost:3002` (alternative frontend instance)
- `http://127.0.0.1:3000` (localhost alternative)
- `http://127.0.0.1:3001` (localhost alternative)
- `http://127.0.0.1:3002` (localhost alternative)

### CSRF Trusted Origins

The same origins are also configured as CSRF trusted origins to allow cross-site requests.

## Files Modified

1. **`env.development`** - Development environment variables
2. **`env.example`** - Example environment file
3. **`setup-dev-env.bat`** - Windows batch script for setup
4. **`setup-dev-env.ps1`** - PowerShell script for setup

## Setup Instructions

### Option 1: Automatic Setup (Recommended)

Run one of the setup scripts:

**Windows Command Prompt:**

```bash
setup-dev-env.bat
```

**PowerShell:**

```powershell
.\setup-dev-env.ps1
```

### Option 2: Manual Setup

1. Copy the development environment file:

   ```bash
   copy env.development .env
   ```

2. Start the Django development server:
   ```bash
   python manage.py runserver
   ```

## Usage

Now you can run your frontend on any of the configured ports:

- **Port 3000:** `npm run dev` (default)
- **Port 3001:** `npm run dev -- -p 3001`
- **Port 3002:** `npm run dev -- -p 3002`

The backend will accept CORS requests from all these ports without any additional configuration.

## Verification

To verify the CORS configuration is working:

1. Check the environment variables:

   ```bash
   python -c "from decouple import config, Csv; print('CORS_ALLOWED_ORIGINS:', config('CORS_ALLOWED_ORIGINS', cast=Csv()))"
   ```

2. Start the Django server and check the console for CORS-related messages

3. Test a frontend request from any of the allowed ports

## Troubleshooting

If you encounter CORS errors:

1. Ensure the `.env` file exists and contains the correct CORS origins
2. Restart the Django development server after changing environment variables
3. Check that the frontend is running on one of the allowed ports
4. Verify that the request is coming from the correct origin

## Security Note

This configuration is for **development only**. In production, you should:

- Use HTTPS origins
- Restrict to specific domains
- Remove localhost/127.0.0.1 origins
- Use environment-specific configuration files
