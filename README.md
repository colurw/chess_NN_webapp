# Chess_NN_webapp

Integrates ensemble_solver.py and the models trained by <a href="https://github.com/colurw/chess_NN/blob/main/readme.md" target="_blank">colurw/chess_NN</a>, into Django web framework.  It allows session-based play through a Gunicorn web server and NGINX reverse proxy.  

It is containerised with Docker.  When spun up, the app is available at http://localhost/play.  It requires 2GB RAM to run.

When updated code is pushed to Github, an Actions Workflow builds the Docker images and pushes them to DockerHub.  These (along with the latest docker-compose.yml file) are then pulled to an AWS EC2 instance and spun up, using the SSH protocol.

Run the app locally using `docker compose -f docker-compose.dev.yml up`

### django web framework
<img src="https://github.com/colurw/chess_NN/assets/66322644/b3d419ff-06b9-4444-85ba-99531d4db79c" align="right" width="300px"/> 
Creates an IP connection to the browser over the Localhost.  When Views.py is 
called by Urls.py, it returns data that populate the Play.html template with the 
current board image and relevant messages.  <br><br>
Form data from the browser are sent back to views.py as POST requests, converted
into tensors, then passed to ensemble_solver(), which returns a tensor representing 
the board-state with the AI response applied.  <br><br>
This tensor is converted by local_chess_tools.py into an image, which can be sent as a base-64 string back to the browser. <br><br>
As the original training data did not include early-game board states, the user had 
to select one of four fully-developed opening options.  The latest update can
handle both player's castling moves, which allows a model trained on whole-game data to be added to the ensemble. 

### web_ensemble_solver.py  
Several neural networks are presented with the same board state.  The 
predicted solutions are combined according to decision criteria to produce an
output that is substantially more accurate than any single neural network is capable 
of producing, analogous to classic wisdom-of-the-crowds quantity estimation findings.

The decision critera check the legality of the raw average of all predictions, if this fails, predictions 
containing illegal moves are removed.  If the new average prediction still does not qualify as a legal move, the most confident legal prediction is chosen, based on an analysis of the probability vectors. If no legal predictions are found, the legal move with the highest cosine similarity to the ensemble's raw average prediction is selected as the new board state. <br clear="right"/>
