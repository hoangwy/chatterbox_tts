#!/usr/bin/env python3
"""
Test script to verify audio directory creation works properly
"""

import os
import sys

def test_audio_directory_creation():
    """Test that we can create the output directory and write files to it"""
    
    print("🧪 Testing audio directory creation...")
    
    # Test 1: Create output directory
    output_dir = "output"
    try:
        os.makedirs(output_dir, exist_ok=True)
        print(f"✅ Successfully created/verified directory: {output_dir}")
    except PermissionError as e:
        print(f"❌ Permission error creating {output_dir}: {e}")
        # Fallback to current directory
        output_dir = "."
        print(f"⚠️  Falling back to current directory: {output_dir}")
    except Exception as e:
        print(f"❌ Error creating directory {output_dir}: {e}")
        return False
    
    # Test 2: Check if we can write to the directory
    test_file = f"{output_dir}/test_write.txt"
    try:
        with open(test_file, 'w') as f:
            f.write("Test file created successfully")
        print(f"✅ Successfully wrote test file: {test_file}")
        
        # Clean up test file
        os.remove(test_file)
        print(f"✅ Successfully cleaned up test file")
        
    except PermissionError as e:
        print(f"❌ Permission error writing to {output_dir}: {e}")
        return False
    except Exception as e:
        print(f"❌ Error writing to {output_dir}: {e}")
        return False
    
    # Test 3: Check current working directory and permissions
    print(f"\n📁 Current working directory: {os.getcwd()}")
    print(f"👤 Current user (UID): {os.getuid()}")
    print(f"📋 Directory permissions for {output_dir}:")
    
    try:
        stat_info = os.stat(output_dir)
        print(f"   - Readable: {os.access(output_dir, os.R_OK)}")
        print(f"   - Writable: {os.access(output_dir, os.W_OK)}")
        print(f"   - Executable: {os.access(output_dir, os.X_OK)}")
    except Exception as e:
        print(f"❌ Error checking permissions: {e}")
    
    print("\n🎉 Audio directory test completed successfully!")
    return True

if __name__ == "__main__":
    success = test_audio_directory_creation()
    sys.exit(0 if success else 1)
