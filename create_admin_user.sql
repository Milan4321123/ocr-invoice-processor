-- Create admin user in Supabase
INSERT INTO public.users (
    username,
    hashed_password,
    email,
    full_name,
    is_active,
    created_at,
    updated_at
) VALUES (
    'admin',
    '$2b$12$H15JMkrTvK9XJpGPahX9fu7BZ/wS6Au69fPRLLBpYksvTAurKspWO',
    'admin@example.com',
    'Administrator',
    true,
    NOW(),
    NOW()
) ON CONFLICT (username) DO UPDATE SET
    hashed_password = EXCLUDED.hashed_password,
    email = EXCLUDED.email,
    full_name = EXCLUDED.full_name,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();
