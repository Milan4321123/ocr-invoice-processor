-- ================================================================
-- STORAGE POLICIES FOR INVOICES BUCKET
-- Run this in Supabase SQL Editor after creating the 'invoices' bucket
-- ================================================================

-- Policy 1: Allow anyone to upload files to invoices bucket
CREATE POLICY "Allow invoice uploads" ON storage.objects
FOR INSERT WITH CHECK (
    bucket_id = 'invoices'
);

-- Policy 2: Allow anyone to view/download files from invoices bucket  
CREATE POLICY "Allow invoice downloads" ON storage.objects
FOR SELECT USING (
    bucket_id = 'invoices'
);

-- Policy 3: Allow anyone to update files in invoices bucket
CREATE POLICY "Allow invoice updates" ON storage.objects
FOR UPDATE USING (
    bucket_id = 'invoices'
) WITH CHECK (
    bucket_id = 'invoices'
);

-- Policy 4: Allow anyone to delete files from invoices bucket
CREATE POLICY "Allow invoice deletions" ON storage.objects  
FOR DELETE USING (
    bucket_id = 'invoices'
);

-- Verify the bucket and policies were created
SELECT 
    'Storage bucket exists' as check_type,
    CASE WHEN EXISTS(SELECT 1 FROM storage.buckets WHERE id = 'invoices') 
         THEN '✅ PASS' 
         ELSE '❌ FAIL' 
    END as status
UNION ALL
SELECT 
    'Storage policies exist' as check_type,
    CASE WHEN (SELECT count(*) FROM pg_policies WHERE schemaname = 'storage' AND policyname LIKE '%invoice%') >= 4
         THEN '✅ PASS'
         ELSE '❌ FAIL'
    END as status;
