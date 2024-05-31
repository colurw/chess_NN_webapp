# Chess_NN_webapp

Integrates ensemble_solver.py and the models trained by <a href="https://github.com/colurw/chess_NN/blob/main/readme.md" target="_blank">colurw/chess_NN</a>, into Django web framework.  It allows session-based play through a Gunicorn web server and NGINX reverse proxy.  

It is containerised with Docker.  When spun up, the app is available at http://localhost/play.  It requires 2GB RAM to run.

When updated code is pushed to Github, an Actions Workflow builds the Docker images and pushes them to DockerHub.  These (along with the latest docker-compose.yml file) are then pulled to an AWS EC2 instance and spun up, using the SSH protocol.

Run it locally using `docker compose -f docker-compose.dev.yml up`

### django web framework
<img src="https://github.com/colurw/chess_NN/assets/66322644/b3d419ff-06b9-4444-85ba-99531d4db79c" align="right" width="300px"/>
Creates an IP connection to the browser over the Localhost.  When Views.py is 
called by Urls.py, it returns data that populate the Play.html template with the 
current board image and relevant messages.  <br><br>
Form data from the browser are sent back to views.py as POST requests, converted
into tensors, then passed to ensemble_solver(), which returns a tensor representing 
the move to be played in response.  <br><br>
This tensor is converted by local_chess_tools.py into an image of the next 
board state, which can be sent as a base64 string back to the browser. <br><br>
As the training data do not include early-game board states, the user must initially 
select from one of four fully-developed opening options.  This avoids the need to 
implement castling - moves of which were excluded from the training dataset to allow 
a less-complex function to encode the raw data. 

### web_ensemble_solver.py  
Several neural networks are presented with the same board state.  The 
predicted solutions are combined according to decision criteria to produce an
output that is substantially more accurate than any single neural network is capable 
of producing, analogous to classic wisdom-of-the-crowds quantity estimation findings.

The decision critera check the legality of the raw average of all predicted moves, before
excluding illegal moves or predictions with disappearing/cloned pieces.  If the average still does not qualify as a legal move, the most confident prediction is chosen, based on an analysis of the probability vectors. If no legal predictions are found, all possible legal moves are calculated using Python Chess library, and the tensor with the highest cosine similarity to the ensemble's raw average prediction is selected as the new board state. <br clear="right"/>
