# Importing packages
from flask import Flask,render_template,redirect,request
from flask_scss import Scss
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# My app
app = Flask(__name__)
Scss(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False
db = SQLAlchemy(app)

class Mytask(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  content = db.Column(db.String(100), nullable=False)
  complete = db.Column(db.Integer,default=0)
  created = db.Column(db.DateTime,default=datetime.utcnow)
  
  def __repr__(self) -> str:
     return f'Task {self.id}'
   
with app.app_context():
  db.create_all()
  
# Homepage
@app.route("/",methods=["POST","GET"])
def index():
    #Add a task
    if request.method == 'POST':
      current_task = request.form['content']
      new_task = Mytask(content = current_task)
      try:
        db.session.add(new_task)
        db.session.commit()
        return redirect('/')
      except Exception as e:
        print(f"Error:{e}")
        return f"Error:{e}"
    
    #See all current tasks
    else:
      tasks = Mytask.query.order_by(Mytask.created).all()
      return render_template('task.html',tasks=tasks)


# Delete an Item
@app.route("/delete/<int:id>")
def delete(id:int):
    delete_task = Mytask.query.get_or_404(id)
    try:
      db.session.delete(delete_task)
      db.session.commit()
      return redirect('/')
    except Exception as e:
      return f"Error:{e}"
    
    
# Update/ Edit an Item
@app.route("/edit/<int:id>",methods=["GET","POST"])
def edit(id:int):
  task = Mytask.query.get_or_404(id)
  if request.method == 'POST':
    task.content = request.form['content']
    try:
      db.session.commit()
      return redirect('/')
    except Exception as e:
      return f"Error:{e}"
  
  else:
    return render_template('edit.html',task=task)
      


# Runner & Debugger
if __name__ == "__main__":
  
  with app.app_context():
    db.create_all()
    
  app.run(debug = True)


