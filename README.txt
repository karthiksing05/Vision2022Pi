This is just a lightweight script I created to process images.

The main function is imageProcessing.get_objects

Run the main.py script to see the function in action, and look at the documentation 
for each method to see how it works.

For now, you can run this script from your laptop to see it working (we will port to a 
Raspberry Pi once we have it and a Pi Camera).

Feel free to tweak params.py to change the params (currently I have chosen the best 
possible for our purposes [red, blue, black] but you can add any colors you want. 
Just remember to update that in the get_objects function.)

make sure to install the requirements.txt file to the environment you're working in
(in most cases just type 'pip install -r requirements.txt' in the cmd line or whatever
prompt you like to use and it'll take care of the rest for you.)

also, red bounds detect fleshy tones sometimes as red. so if you want to test red,
it would probably be best to use tongs or tweezers to hold something in front of the camera.
In a real-world scenario, where the background is constant and there are no fleshy tones in
the game arena, this won't matter, but be careful all the same.