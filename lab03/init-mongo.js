// Initialize the notes database and collection
db = db.getSiblingDB('notesdb');

// Create the notes collection
db.createCollection('notes');

// Create index on created_at field for better query performance
db.notes.createIndex({ "created_at": -1 });

// Insert sample data
db.notes.insertMany([
    {
        title: "Welcome Note",
        content: "This is your first note! Welcome to the Notes API.",
        created_at: new Date(),
        updated_at: new Date()
    },
    {
        title: "Getting Started",
        content: "You can create, read, update, and delete notes using the API endpoints.",
        created_at: new Date(),
        updated_at: new Date()
    }
]);

print("Database initialized successfully!");