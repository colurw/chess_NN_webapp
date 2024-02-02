# Chess_NN_webapp

Uses the trained models and ensemble_solver.py from <a href="https://github.com/colurw/chess_NN/blob/main/readme.md" target="_blank">Chess_NN</a> and Django web framework.  It allows session-based play through a Gunicorn web server and NGINX reverse proxy.  It is containerised with Docker.  When spun up, the app is available at http://localhost/play.  It requires 4GB RAM to run. 

### django web framework
<img src="https://github.com/colurw/chess_NN/assets/66322644/b3d419ff-06b9-4444-85ba-99531d4db79c" align="right" width="300px"/>
Creates an IP connection to the browser over the Localhost.  When Views.py is 
called by Urls.py, it returns data that populate the Index.html template with the 
current board image and relevant messages.  <br><br>
Form data from the browser are sent back to views.py as POST requests, converted
into tensors, then passed to Ensemble_solver(), which returns a tensor representing 
the move to be played in response.  <br><br>
This tensor is converted by Local_chess_tools.py into an image of the next 
board state, and then into a base64 string, which can be sent as an argument of 
HttpRequest() back to Index.html <br><br>
As the training data do not include early-game board states, the user must initially 
select from one of three fully-developed opening options.  This avoids having to 
implement a castling feature - moves of which were also excluded from the training 
dataset to allow less-complex functions when encoding raw training data. 

### web_ensemble_solver.py  
Several neural networks are presented with the same board state.  The 
predicted solutions are combined according to decision criteria to produce an
output that is substantially more accurate than any single neural network is capable 
of producing, analogous to classic wisdom-of-the-crowds quantity estimation findings.

The decision critera check the legality of the raw average of all predicted moves, before
excluding illegal moves or predictions with disappearing/cloned pieces.  If the average still
does not qualify as a legal move, the most confident prediction is chosen, based on an analysis
of the probability vectors. If no legal predictions are found, the ensemble resort to a random 
choice from a list of all legal moves. <br clear="right"/>
