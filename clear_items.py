import sqlite3

def clear_all_items():
    """Delete all contents from the items table"""
    try:
        # Connect to the database
        conn = sqlite3.connect('items.db')
        cursor = conn.cursor()
        
        # Delete all records from the items table
        cursor.execute("DELETE FROM items")
        
        # Commit the changes
        conn.commit()
        
        # Get the number of deleted rows
        deleted_count = cursor.rowcount
        print(f"Successfully deleted {deleted_count} items from the database.")
        
        # Close the connection
        conn.close()
        
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    clear_all_items()
