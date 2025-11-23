def menu():
    print("1. Run Simple Face Detection (face.py)")
    print("2. Run AI Focus Assistant (smart_assistant.py)")
    print("3. Run Simple Voice Assistant (voice_assistant.py)")
    print("4. Run Simple Face Detection with counts (face_count.py)")
    print("5. Exit")

while True:
    menu()
    choice = input("Select an option: ")
    if choice == '1':
        import face
        face.run_face_detection()
    elif choice == '2':
        import smart_assistant
        smart_assistant.run_smart_assistant() 
    elif choice == '3':
        import voice_assistant
        voice_assistant.run_assistant()
    elif choice == '4':
        import face1
        face1.get_face_unfocus_count()
    elif choice == '5':
        print("Exiting the program.")
        break
    else :
        print("Invalid choice. Please try again.")