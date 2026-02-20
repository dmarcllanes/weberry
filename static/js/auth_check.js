// Shared authentication check for Supabase
// Included on pages where we want to auto-redirect if the user is already logged in (e.g. Landing, Login)

let supabaseClient;

function getSupabase() {
    if (supabaseClient) return supabaseClient;
    const sb = (typeof supabase !== 'undefined') ? supabase : window.supabase;
    if (sb && window.SUPABASE_URL && window.SUPABASE_KEY) {
        supabaseClient = sb.createClient(window.SUPABASE_URL, window.SUPABASE_KEY);
    }
    return supabaseClient;
}

async function syncSession(session) {
    try {
        console.log('Syncing session for user:', session.user.email);
        const response = await fetch('/api/auth/session', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                access_token: session.access_token,
                refresh_token: session.refresh_token,
                user_id: session.user.id,
                email: session.user.email,
                full_name: session.user.user_metadata?.full_name || null,
                avatar_url: session.user.user_metadata?.avatar_url || session.user.user_metadata?.picture || null
            }),
        });

        if (response.ok) {
            console.log('Session synced, redirecting to dashboard...');
            window.location.href = '/pages';
        } else {
            console.error('Session sync failed:', response.status);
        }
    } catch (err) {
        console.error('Session sync error:', err);
    }
}

window.addEventListener('load', async () => {
    // Check if we are on the landing page or login page
    // If we have a hash with access_token (from Google redirect), Supabase parses it automatically.

    const client = getSupabase();
    if (!client) {
        console.warn('Supabase not initialized in auth_check.js');
        return;
    }

    // Check if we just logged out
    const params = new URLSearchParams(window.location.search);
    if (params.get('logged_out') === '1') {
        console.log('User logged out, clearing Supabase session...');
        await client.auth.signOut();
        // Clean up the URL to avoid loop if user refreshes
        window.history.replaceState({}, '', '/');
        return;
    }

    // Check for existing session
    const { data: { session } } = await client.auth.getSession();
    if (session) {
        await syncSession(session);
        return;
    }

    // Listen for auth changes (e.g. just redirected from Google)
    client.auth.onAuthStateChange(async (event, session) => {
        if (event === 'SIGNED_IN' && session) {
            await syncSession(session);
        }
    });
});
