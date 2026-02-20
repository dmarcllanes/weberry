// Initialize Supabase client lazily — CDN may not be ready at parse time
let supabaseClient;

function getSupabase() {
    if (supabaseClient) return supabaseClient;
    const sb = (typeof supabase !== 'undefined') ? supabase : window.supabase;
    if (sb) {
        supabaseClient = sb.createClient(window.SUPABASE_URL, window.SUPABASE_KEY);
        console.log('Supabase initialized');
    }
    return supabaseClient;
}

// Google sign-in button
document.addEventListener('DOMContentLoaded', () => {
    const googleBtn = document.getElementById('googleBtn');
    if (googleBtn) {
        googleBtn.addEventListener('click', async () => {
            const client = getSupabase();
            if (!client) {
                console.error('Supabase client not initialized');
                alert('System error: Supabase not initialized. Check console.');
                return;
            }
            googleBtn.disabled = true;
            googleBtn.textContent = 'Redirecting...';

            const { data, error } = await client.auth.signInWithOAuth({
                provider: 'google',
                options: {
                    queryParams: {
                        access_type: 'offline',
                        prompt: 'consent',
                    },
                    redirectTo: window.location.origin + '/login'
                }
            });

            if (error) {
                console.error('Google login error:', error);
                alert('Login failed: ' + error.message);
                googleBtn.disabled = false;
                googleBtn.textContent = 'Continue with Google';
            }
        });
    } else {
        console.error('Google button NOT found');
    }
});

// After Google redirect, detect session and sync to backend
async function syncSession(session) {
    try {
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
            window.location.href = '/pages';
        }
    } catch (err) {
        console.error('Session sync error:', err);
    }
}

window.addEventListener('load', async () => {
    const client = getSupabase();
    if (!client) return;

    // If we just logged out, clear Supabase client session too
    const params = new URLSearchParams(window.location.search);
    if (params.get('logged_out') === '1') {
        await client.auth.signOut();
        // Clean up the URL
        window.history.replaceState({}, '', '/login');
        return;
    }

    const { data: { session } } = await client.auth.getSession();
    if (session) {
        await syncSession(session);
        return;
    }

    client.auth.onAuthStateChange(async (event, session) => {
        if (event === 'SIGNED_IN' && session) {
            await syncSession(session);
        }
    });
});
