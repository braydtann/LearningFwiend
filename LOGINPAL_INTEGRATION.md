# LoginPal OAuth Integration

This document outlines the LoginPal OAuth integration implementation for LearningFwiend LMS.

## Current Status: PLACEHOLDER IMPLEMENTATION

The LoginPal OAuth integration is currently implemented as a placeholder while the LoginPal service is being deployed on the Emergent platform. The UI and backend endpoints are ready for integration once LoginPal becomes available.

## Frontend Implementation

### Components
- **LoginPalButton** (`/frontend/src/components/auth/LoginPalButton.js`)
  - Professional OAuth button with loading states
  - Status indicator showing deployment pending
  - Ready for easy replacement with real OAuth flow

### Services
- **loginPalService** (`/frontend/src/services/loginPalService.js`)
  - Complete service class for LoginPal API interactions
  - Methods for OAuth flow, user management, and webhooks
  - Placeholder implementations ready for real API calls

### UI Integration
- Added to Login page with proper styling
- Positioned prominently above demo login options
- Includes visual feedback and status indicators

## Backend Implementation

### API Endpoints (All Placeholder)

#### Authentication Endpoints
- `GET /api/auth/loginpal/status` - Service status check
- `GET /api/auth/loginpal/login` - OAuth initiation
- `POST /api/auth/loginpal/callback` - OAuth callback handler

#### User Management
- `GET /api/auth/loginpal/users` - Get synced users
- `POST /api/auth/loginpal/sync-user` - Sync user data
- `PUT /api/auth/loginpal/user-role` - Update user roles

#### Webhook Support
- `POST /api/auth/loginpal/webhook` - Webhook endpoint for LoginPal events
- `GET /api/auth/loginpal/webhooks` - View webhook history

### Data Models
- **LoginPalUser** - User data structure
- **LoginPalWebhook** - Webhook event structure  
- **UserRoleUpdate** - Role management structure

### Database Collections
- `loginpal_users` - Synced user data
- `loginpal_webhooks` - Webhook event log

## Expected LoginPal Integration Flow

1. **OAuth Authentication**
   ```
   User clicks "Continue with LoginPal" 
   → Redirect to LoginPal authorization
   → User authorizes application
   → LoginPal redirects to callback with auth code
   → Backend exchanges code for tokens
   → User session established with role/permissions
   ```

2. **Role & Permission Management**
   - LoginPal will manage user roles (admin, instructor, learner)
   - Permissions will be synced via webhooks or API calls
   - LMS will respect LoginPal role assignments

3. **User Synchronization**
   - New users created via OAuth callback
   - Existing users updated via webhooks
   - Role changes propagated in real-time

4. **Webhook Events**
   - `user.created` - New user registration
   - `user.updated` - Profile changes
   - `user.deleted` - Account deletion
   - `role.changed` - Role/permission updates

## Required LoginPal Configuration

When LoginPal is deployed, the following configuration will be needed:

### OAuth Application Settings
- **Client ID**: Provided by LoginPal
- **Client Secret**: Provided by LoginPal (store in backend .env)
- **Redirect URI**: `{FRONTEND_URL}/oauth/callback`
- **Scopes**: `openid profile email roles`

### Webhook Configuration
- **Webhook URL**: `{BACKEND_URL}/api/auth/loginpal/webhook`
- **Events**: user.created, user.updated, user.deleted, role.changed
- **Security**: Webhook signature verification (to be implemented)

### Environment Variables

Backend `.env` additions needed:
```bash
# LoginPal OAuth Configuration
LOGINPAL_CLIENT_ID=your_client_id_here
LOGINPAL_CLIENT_SECRET=your_client_secret_here
LOGINPAL_AUTHORIZE_URL=https://auth.loginpal.emergent.com/oauth2/authorize
LOGINPAL_TOKEN_URL=https://auth.loginpal.emergent.com/oauth2/token  
LOGINPAL_USER_INFO_URL=https://api.loginpal.emergent.com/user
LOGINPAL_WEBHOOK_SECRET=your_webhook_secret_here

# JWT Configuration for LoginPal tokens
JWT_SECRET_KEY=your_jwt_secret_key_here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30
```

## Security Considerations

1. **CSRF Protection**: State parameter validation in OAuth flow
2. **Token Security**: JWT tokens with proper expiration
3. **Webhook Verification**: Signature validation for webhook events  
4. **HTTPS**: All OAuth communications must use HTTPS in production
5. **Scope Limitation**: Request minimal required OAuth scopes

## Testing Strategy

### Current Placeholder Testing
- Button click shows appropriate "coming soon" message
- Backend endpoints return placeholder responses
- Webhook storage works for future processing

### Future Integration Testing
- Complete OAuth flow end-to-end
- Role synchronization accuracy
- Webhook event processing
- Error handling and edge cases
- Security vulnerability testing

## Migration Path

When LoginPal becomes available:

1. **Backend Updates**
   - Add environment variables
   - Replace placeholder logic with real OAuth client
   - Implement JWT token management
   - Add webhook signature verification

2. **Frontend Updates**  
   - Update `loginPalService` with real API calls
   - Add OAuth callback page/component
   - Remove placeholder messaging
   - Add proper error handling

3. **Database Updates**
   - Create proper indexes for user lookup
   - Add data migration for existing users
   - Set up webhook event processing queues

4. **Infrastructure**
   - Configure OAuth redirect URLs
   - Set up webhook endpoints with proper security
   - Add monitoring and logging

## Files Modified/Created

### Frontend
- `/frontend/src/pages/Login.js` - Added LoginPal button
- `/frontend/src/components/auth/LoginPalButton.js` - OAuth button component
- `/frontend/src/services/loginPalService.js` - LoginPal API service

### Backend
- `/backend/server.py` - Added placeholder endpoints and models

### Documentation
- `/LOGINPAL_INTEGRATION.md` - This file

## Next Steps

1. **Wait for LoginPal Deployment** - Service needs to be available on Emergent platform
2. **Obtain OAuth Credentials** - Get client ID and secret from LoginPal
3. **Configure Webhook URLs** - Set up webhook endpoints in LoginPal dashboard
4. **Replace Placeholder Logic** - Implement real OAuth flow
5. **Security Review** - Audit OAuth implementation
6. **End-to-End Testing** - Test complete integration flow

---

**Status**: Ready for LoginPal deployment
**Last Updated**: December 2024
**Integration Type**: OAuth 2.0 Authorization Code Flow