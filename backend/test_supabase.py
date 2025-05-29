import os
from dotenv import load_dotenv
from supabase import create_client, Client

def test_supabase_connection():
    """Test Supabase connection with credentials from .env file"""
    # Load environment variables
    load_dotenv()
    
    # Get Supabase credentials
    url = os.getenv("SUPA_URL")
    key = os.getenv("SUPA_KEY")
    
    print(f"Testing Supabase connection...")
    print(f"URL found: {'Yes' if url else 'No'}")
    print(f"Key found: {'Yes' if key else 'No'}")
    
    if not url or not key:
        print("❌ ERROR: Missing Supabase credentials in .env file")
        return False
    
    try:
        # Initialize Supabase client
        supabase = create_client(url, key)
        print(f"✅ Successfully connected to Supabase!")
        
        # Test each component separately
        try:
            # Test storage
            print("\nTesting Storage API...")
            storage = supabase.storage
            print("✅ Storage API accessible")
            
            # Create "invoices" bucket if it doesn't exist
            try:
                bucket_id = "invoices"
                storage.create_bucket(bucket_id, {"public": True})
                print(f"✅ Created new 'invoices' bucket")
            except Exception as e:
                if "already exists" in str(e):
                    print(f"✅ 'invoices' bucket already exists")
                else:
                    print(f"⚠️ Unable to create bucket: {str(e)}")
        except Exception as e:
            print(f"❌ Error with Storage API: {str(e)}")
        
        # Test database
        try:
            print("\nTesting Database API...")
            # Try to list tables
            response = supabase.table("invoices").select("*").limit(1).execute()
            print(f"✅ Successfully queried 'invoices' table")
            print(f"Found {len(response.data)} records in 'invoices' table")
        except Exception as e:
            print(f"❌ Error querying 'invoices' table: {str(e)}")
            print("You may need to create the 'invoices' table with this SQL:")
            print("""
CREATE TABLE public.invoices (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  filename text NOT NULL,
  url text,
  status text DEFAULT 'uploaded',
  file_size bigint,
  created_at timestamptz DEFAULT now()
);
            """)
        
        # Test file upload
        try:
            print("\nTesting file upload...")
            # Create a temporary test file
            test_file_content = b"%PDF-1.4\nTest PDF content\n%%EOF"
            test_file_name = "test_upload.pdf"
            
            with open(test_file_name, "wb") as f:
                f.write(test_file_content)
            
            # Upload the file
            with open(test_file_name, "rb") as f:
                storage.from_("invoices").upload(test_file_name, f)
            
            print(f"✅ Successfully uploaded test file to 'invoices' bucket")
            
            # Clean up
            os.remove(test_file_name)
            storage.from_("invoices").remove([test_file_name])
            print(f"✅ Cleaned up test file")
        except Exception as e:
            print(f"❌ Error testing file upload: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR connecting to Supabase: {str(e)}")
        print("Check your credentials and network connection")
        return False

if __name__ == "__main__":
    test_supabase_connection()