# GitHub Webhook Monitor with Supabase

A Flask application that receives GitHub webhooks and displays repository activities in real-time using Supabase as the database.

## Features

- ✅ Receives GitHub webhooks for Push, Pull Request, and Merge events
- ✅ Stores event data in Supabase (PostgreSQL)
- ✅ Real-time UI that polls for updates every 15 seconds
- ✅ Clean, responsive web interface
- ✅ Support for all required event formats
- ✅ Modern PostgreSQL database with excellent performance

## Project Structure

```
webhook-repo/
├── app.py                 # Main Flask application
├── templates/
│   └── index.html        # UI template
├── requirements.txt      # Python dependencies
├── README.md            # This file
└── .env                 # Environment variables (create this)
```

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/pratikwayal01/webhook-repo.git
cd webhook-repo
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Supabase

1. **Create a Supabase Account**
   - Go to [supabase.com](https://supabase.com)
   - Sign up for a free account
   - Create a new project

2. **Get Your Credentials**
   - Go to your project dashboard
   - Navigate to `Settings` → `API`
   - Copy your `Project URL` and `anon/public` key

3. **Create the Database Table**
   - Go to `SQL Editor` in your Supabase dashboard
   - Run this SQL to create the table:

```sql
CREATE TABLE github_actions (
    id SERIAL PRIMARY KEY,
    action VARCHAR(50) NOT NULL,
    author VARCHAR(255) NOT NULL,
    from_branch VARCHAR(255),
    to_branch VARCHAR(255) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    request_id VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add indexes for better performance
CREATE INDEX idx_github_actions_timestamp ON github_actions(timestamp DESC);
CREATE INDEX idx_github_actions_action ON github_actions(action);
```

### 4. Environment Configuration

Create a `.env` file in the root directory:

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here
FLASK_ENV=development
FLASK_DEBUG=True
```

Replace `your-project-id` and `your-anon-key-here` with your actual Supabase credentials.

### 5. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

## Setting Up GitHub Webhooks

### Step 1: Deploy Your Webhook Endpoint

For testing, you can use tools like:
- **ngrok**: `ngrok http 5000` (for local development)
- **Vercel**: Deploy to Vercel for a public URL
- **Railway**: Deploy to Railway for a public URL
- **Heroku**: Deploy to Heroku for a public URL

### Step 2: Configure GitHub Webhook

1. Go to your `action-repo` repository on GitHub
2. Navigate to `Settings` > `Webhooks`
3. Click `Add webhook`
4. Set the following:
   - **Payload URL**: `https://your-domain.com/webhook`
   - **Content type**: `application/json`
   - **Secret**: (optional, but recommended)
   - **Events**: Select individual events:
     - ✅ Pushes
     - ✅ Pull requests

### Step 3: Test the Integration

1. Make a push to your `action-repo`
2. Create a pull request
3. Merge a pull request
4. Check your webhook receiver UI at `http://localhost:5000`

## API Endpoints

- `GET /` - Main UI page
- `POST /webhook` - GitHub webhook receiver
- `GET /api/actions` - JSON API for recent actions
- `GET /health` - Health check endpoint
- `POST /setup-database` - Database setup helper (development only)

## Event Formats

The application displays events in the following formats:

### Push Events
**Format**: `{author} pushed to {to_branch} on {timestamp}`  
**Example**: "Travis pushed to staging on 1st April 2021 - 9:30 PM UTC"

### Pull Request Events
**Format**: `{author} submitted a pull request from {from_branch} to {to_branch} on {timestamp}`  
**Example**: "Travis submitted a pull request from staging to master on 1st April 2021 - 9:00 AM UTC"

### Merge Events
**Format**: `{author} merged branch {from_branch} to {to_branch} on {timestamp}`  
**Example**: "Travis merged branch dev to master on 2nd April 2021 - 12:00 PM UTC"

## Database Schema

The application stores events in Supabase with the following schema:

```sql
CREATE TABLE github_actions (
    id SERIAL PRIMARY KEY,
    action VARCHAR(50) NOT NULL,         -- 'push', 'pull_request', 'merge'
    author VARCHAR(255) NOT NULL,        -- GitHub username
    from_branch VARCHAR(255),            -- Source branch (null for push)
    to_branch VARCHAR(255) NOT NULL,     -- Target branch
    timestamp TIMESTAMPTZ NOT NULL,      -- When the event occurred
    request_id VARCHAR(255),             -- Commit ID or PR number
    created_at TIMESTAMPTZ DEFAULT NOW() -- When record was created
);
```

## Advantages of Using Supabase

✅ **Real-time capabilities** - Built-in real-time subscriptions  
✅ **PostgreSQL power** - Full SQL support with excellent performance  
✅ **Built-in auth** - Ready for user authentication if needed  
✅ **Auto-generated APIs** - REST and GraphQL APIs out of the box  
✅ **Dashboard** - Easy data management through web interface  
✅ **Free tier** - Generous free tier for development and testing  
✅ **Instant deployment** - No database setup required  

## Troubleshooting

### Common Issues

1. **Supabase Connection Error**
   - Verify your `SUPABASE_URL` and `SUPABASE_KEY` in `.env`
   - Check if the table `github_actions` exists
   - Ensure your Supabase project is active

2. **Table Not Found Error**
   - Run the SQL table creation script in Supabase dashboard
   - Or use the `/setup-database` endpoint for help

3. **Webhook Not Receiving Events**
   - Verify your webhook URL is publicly accessible
   - Check GitHub webhook delivery logs
   - Ensure content type is set to `application/json`

4. **UI Not Updating**
   - Check browser console for JavaScript errors
   - Verify the `/api/actions` endpoint returns data
   - Ensure Supabase has stored events

### Logs and Debugging

The application prints helpful logs to the console:
- Supabase connection status
- Incoming webhook events
- Event processing results
- API requests

Check the `/health` endpoint to verify database connectivity.

## Deployment Options

### Vercel Deployment (Recommended)

1. Install Vercel CLI:
   ```bash
   npm i -g vercel
   ```

2. Create `vercel.json`:
   ```json
   {
     "functions": {
       "app.py": {
         "runtime": "python3.9"
       }
     },
     "routes": [
       {
         "src": "/(.*)",
         "dest": "app.py"
       }
     ]
   }
   ```

3. Deploy:
   ```bash
   vercel --prod
   ```

4. Set environment variables in Vercel dashboard

### Railway Deployment

1. Connect your GitHub repository to Railway
2. Set environment variables:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
3. Deploy automatically on git push

### Heroku Deployment

1. Create a `Procfile`:
   ```
   web: gunicorn app:app
   ```

2. Deploy to Heroku:
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

3. Set environment variables:
   ```bash
   heroku config:set SUPABASE_URL=your-supabase-url
   heroku config:set SUPABASE_KEY=your-supabase-key
   ```

## Testing

You can test webhook events manually using curl:

```bash
# Test push event
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: push" \
  -d '{
    "pusher": {"name": "TestUser"},
    "ref": "refs/heads/main",
    "head_commit": {"id": "abc123"}
  }'

# Check if data was stored
curl http://localhost:5000/api/actions
```

## Monitoring with Supabase

- **Real-time monitoring**: View data changes in Supabase dashboard
- **Performance metrics**: Built-in performance monitoring
- **Query optimization**: Use the query analyzer for performance tuning
- **Backups**: Automatic backups on paid plans

## Advanced Features

### Real-time Updates (Optional Enhancement)

You can enhance the UI to use Supabase real-time subscriptions instead of polling:

```javascript
// Example of real-time subscription (advanced)
const supabase = createClient(supabaseUrl, supabaseKey)

supabase
  .channel('github_actions')
  .on('postgres_changes', { 
    event: 'INSERT', 
    schema: 'public', 
    table: 'github_actions' 
  }, (payload) => {
    // Update UI immediately when new events arrive
    addNewActionToUI(payload.new)
  })
  .subscribe()
```

## Security Considerations

- **API Key Security**: Never expose your `service_role` key in client-side code
- **RLS (Row Level Security)**: Consider enabling RLS for production use
- **Webhook Validation**: Add GitHub webhook secret validation for production
- **Rate Limiting**: Implement rate limiting for webhook endpoints

## License

This project is for assessment purposes.

## Support

If you encounter any issues:
1. Check application logs in the console
2. Verify Supabase connection in the dashboard
3. Check GitHub webhook delivery logs
4. Test the `/health` endpoint
5. Review Supabase project logs

---

**Note**: This application uses Supabase for modern, scalable data storage with excellent developer experience. The PostgreSQL backend provides superior performance and SQL capabilities compared to traditional NoSQL solutions.