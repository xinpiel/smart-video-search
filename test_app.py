import streamlit as st

def main():
    st.title("Test App")
    st.write("Hello, World!")
    st.write("If you can see this, Streamlit is working!")
    
    # Add some interactive elements
    if st.button("Click me!"):
        st.success("Button clicked!")
    
    number = st.slider("Select a number", 0, 100)
    st.write(f"You selected: {number}")

if __name__ == "__main__":
    main() 