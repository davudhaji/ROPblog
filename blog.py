from flask import Flask,render_template,flash,redirect,url_for,session,logging,request
from wtforms import Form,StringField,PasswordField,validators,TextAreaField
from passlib.hash import sha256_crypt
from functools import wraps
import os
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

#Register Class
class RegisterForm(Form):
    name = StringField("Ad Soyad",validators=[validators.Length(min=4, max=25),validators.DataRequired()])
    username = StringField("İsdifadəci Adı",validators=[validators.Length(min=4, max=25),validators.DataRequired()])
    email = StringField("Email",validators=[validators.Length(min=7,max=35),validators.Email(),validators.DataRequired()])
    
    password = PasswordField("Parol",validators=[
        validators.DataRequired(message="Xahiş Olunur Parol Daxil Edesiniz."),
        validators.EqualTo(fieldname="confirm"),
        
    ])
    confirm=PasswordField("Təkrar Parol",validators=[validators.DataRequired(message="Təkrar Parol u Daxil Edin.")])
    



class Login(Form):
    username=StringField("İsdifadəci Adı",[validators.DataRequired(message="Username i Daxil Edin")])
    password = PasswordField("Parol",[validators.DataRequired(message="Parolu Daxil Edin.")])




class Article(Form):
    title = StringField("Başlıq",validators=[validators.DataRequired(message="Başlıqı Daxil Edin")])
    content = TextAreaField("Məzmun",validators=[validators.DataRequired(message="Məzmun Doldurun")])
    #contenti ona gore TextAreaField nen duzeltdikki content cox yer tutatcaq yeni icinde metn olacaq ona gorede TextAreaField den isdifade etdik.

class updateProfil(Form):
    name = StringField("Ad Soyad",validators=[validators.Length(min=4, max=25),validators.DataRequired()])
    username = StringField("İsdifadəci Adı",validators=[validators.Length(min=4, max=25),validators.DataRequired()])
    email = StringField("Email",validators=[validators.Length(min=7,max=35),validators.Email(),validators.DataRequired()])
    
    password = PasswordField("Parol",validators=[
        validators.EqualTo(fieldname="confirm"),
        
    ])
    confirm=PasswordField("Təkrar Parol")





app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////rop.db'
db = SQLAlchemy(app)

app.secret_key="davudblog19"



socketio = SocketIO( app )



def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged" in session:
            return f(*args,**kwargs)

        else:
            flash("Ilk öncə isdifadəçi kimi daxil olun","danger")
            return redirect(url_for("login"))

        #return f(*args, **kwargs)
    return decorated_function



class users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    username = db.Column(db.String(80))
    email = db.Column(db.String(80))
    password = db.Column(db.String(80))
    photo = db.Column(db.String)

class chatroom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    message = db.Column(db.String)
    date = db.Column(db.DateTime,nullable=False,default=datetime.utcnow)

class Articles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    content = db.Column(db.Text)
    author = db.Column(db.String(80))
    author_id = db.Column(db.Integer)
    time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    photo = db.Column(db.String)



def checkEdit(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "id" in session:

            ID=int(kwargs["id"])
            data = Articles.query.filter_by(id=ID).first()
            print("TRUEEEE")
            if data.author_id==session["id"]:
                print("TRUEEEE")
                return f(*args, **kwargs)

        flash("Siz Bu Meqaləyə Baxa Bilməzsiniz","danger")
        return redirect(url_for("mainPage"))
    return decorated_function



@app.route("/")
def mainPage():
 

    return render_template("index.html")






@app.route("/about")
def aboutPage():
    return render_template("about.html")




@app.route("/addArticle",methods=["GET","POST"])
@login_required
def addArticle():
    meqale = Article(request.form)
    if request.method=="POST":
        title = meqale.title.data
        content = meqale.content.data
        author = session["username"]
        author_id = session["id"]
        File = request.files["file"]
        FileName=File.filename
        if FileName:   
            File.save(os.path.join("static/articlePhoto/",FileName))         

            article = Articles()
            article.title=title
            article.author=author
            article.content=content
            article.author_id=author_id
            article.photo = FileName

            db.session.add(article)
            db.session.commit()

            flash("Məqalənız Uğurla Yayınlandı.","success1")
            return redirect(url_for("mainPage"))



        article = Articles()
        article.title = title
        article.author = author
        article.content = content
        article.author_id = author_id
        article.photo = "default.jpg"

        db.session.add(article)
        db.session.commit()

        flash("Məqalənız Uğurla Yayınlandı.","success1")
        return redirect(url_for("mainPage"))
        

    return render_template("addArticle.html",form=meqale)


@app.route("/articles/<string:id>")
def idArticles(id):

    result =Articles.query.filter_by(id=id).first()
    if result:
        data = result
        return render_template("article.html",data=data)
    return redirect(url_for("articles"))


@app.route("/login",methods=["GET","POST"])
def login():
    login1 = Login(request.form)
    if request.method=="GET":

        return render_template("login.html",form=login1)

    else:
        username=login1.username.data
        password=login1.password.data


        
        result=users.query.filter_by(username=username).first()



        if result:
            uzunluq=0
            allData=result
            print(allData,'allllDaaaataa')
            data=allData
            print(data,"dataaaa")
            if 1:#len(allData)==1
                realPass=data.password

                if sha256_crypt.verify(password,realPass):
                    ID = data.id
                    session["logged"]=True # burda loggedi vu usernamenin icine ne isdesek
                    session["username"]=username # vere bilerik ama gerek navbarda da eynisin verek.
                    session["id"]=ID
                    session["name"]=data.name
                
            
                    flash("Uğurla Giriş Etdiniz!","success1")
                    return redirect(url_for("mainPage"))
                else:
                    flash("Parolulunuz Yanlışdır!","danger")
                    return redirect(url_for("login"))

            
        else:
            flash("Belə İsdifadəci Adı Yoxdur","danger")
            return redirect(url_for("login"))




# Acauntdan Cixis
@app.route("/logout")
def Logout():
    session.clear()# bunu sesionun icindekileri temizdey ucun yazidqki acauntdan cixa bilek
    return redirect(url_for("mainPage"))





@app.route("/articles")
def articles():

    result= Articles.query.all()
    
    if result:
        data = result
        uzun=len(data)
        image_file = os.path.join("../static/articlePhoto/")
        return render_template("articles.html",data = data,len=uzun,image_loc=image_file)

    return render_template("articles.html")




@app.route("/control")
@login_required
def Control():

    yoxla = Articles.query.filter_by(author_id=session["id"]).all()
    print(yoxla,"yoxlaaa")

    if yoxla:
        data = yoxla
        return render_template("controlPanel.html",data=data,len=len(data))

    return render_template("controlPanel.html",len=False)

@app.route("/register",methods=["GET","POST"])
def register():
    reqister1 = RegisterForm(request.form) #burda Register in icindeki request.form reqister seyfesindeki melumatlari ozunde saxlayir
    

    if request.method=="POST":
        
        name = reqister1.name.data
        username = reqister1.username.data
        email = reqister1.email.data
        #password = sha256_crypt.encrypt(reqister1.password.data)
        password = reqister1.password.data
        confirm = reqister1.confirm.data
        data11 = users.query.all()

        for i in data11:
            if i.username==username:
                flash("Xəta Baş Verdi. Belə bir isdifadəçi adı mövcuddur.", "danger")
                return redirect(url_for("register"))


        if len(name)<5 or len(username)<5 or password!=confirm or len(password)<5 or len(email)<7 or not("@" in email):

            flash("Xəta Baş Verdi.  Xanaları Düzgün Doldurun.","danger")
            return redirect(url_for("register"))


        else:

            password = sha256_crypt.encrypt(password)
            newUser=users(name=name,email=email,username=username,password=password,photo="default.png")
            db.session.add(newUser)
            db.session.commit()

            flash("Uğurla Qeydiyatdan Keçdiniz.","success")
            return redirect(url_for("mainPage"))


    elif request.method=="GET":
        return render_template("register.html",form=reqister1)




@app.route("/edit/<string:id>",methods=["GET","POST"])
@checkEdit
@login_required
def EditArticle(id):
    if id:
        print("IDE E DAXIL OLDU")
        if request.method=="GET":
            print("REQUESTE E DAXIL OLDU")

            result = Articles.query.filter_by(id=id).first()
            print(result.title,"tittle")
            if result:
                data = result
                article = Article()
                article.title.data = data.title
                article.content.data = data.content

                return render_template("editArticle.html",form=article)
            flash("Bu Məqaləyə Yetki Yoxdur","danger")
            return redirect(url_for("mainPage"))
        else:
            newdata=Article(request.form)
            newTitle = newdata.title.data
            newContent = newdata.content.data

            data = Articles.query.filter_by(id=id).first()
            data.content=newContent
            data.title=newTitle

            db.session.commit()
        
            image_loc=request.files["file"]
            image_name=image_loc.filename
            print(image_name)


            oldImage=data.photo
            
            allowList=[".jpg",".gif",".png"]
            #save
            if image_name and  image_name[-4:] in allowList:
                print("daxilll",oldImage)
                if oldImage == "default.jpg":
                    sonad=(str(id)+image_name)
                    image_loc.save(os.path.join("static/articlePhoto/",sonad))

                    data.photo=sonad
                    db.session.commit()

                else:
                    sonad=(str(id)+image_name)

                    image_loc.save(os.path.join("static/articlePhoto/",sonad))
                    os.chdir("static/articlePhoto")
                    os.remove(oldImage)
                    os.chdir("../../")

                    data.photo = sonad
                    db.session.commit()

                flash("Güncenlendi","success2")
                return redirect(url_for("Control"))
    flash("Yeniləndi","success2")
    return redirect(url_for("mainPage"))


@app.route("/delete/<string:id>")
@login_required
def Delete(id):

    result = Articles.query.filter_by(id=int(id),author_id=int(session["id"])).first()

    if result:
        data = result

        db.session.delete(data)
        db.session.commit()

        flash("Silindi!","success2")
        return redirect(url_for("Control"))
    print(id,type(id))
    flash("Sizin Bele Bir Məqaləniz Yoxdur!","danger")
    return redirect(url_for("mainPage"))
    



@app.route("/search",methods=["GET","POST"])
def search():
    if request.method=="POST":
        data = request.form.get("text") #burda dedikki requestle(sorguyla) birlikde gelen articlenin icerisindeki form un  icindeki adi text e baraber olan melumati dataya beraber et
        search1="%{}%".format(data)
        result = Articles.query.filter(Articles.title.like(search1)).all()

        if result and data!="":
            image_file = os.path.join("../static/articlePhoto/")
            new = result
            print(data)
            return render_template("search.html",data=new,len=len(new),image_file=image_file)
        
        return render_template("search.html",data=False,len=0)


    return redirect(url_for("mainPage"))



@app.route("/profil",methods=["POST","GET"])
@login_required
def profil():
    if request.method=="GET":

        data = users.query.filter_by(id=session["id"]).first()

        image_loc=data.photo

        


        return render_template("profil.html",image_file=os.path.join("static/image/",image_loc),data=data)
    
    else:
        adphoto=users.query.filter_by(id=session["id"]).first()

       
        kohne = adphoto.photo
        if "file" in request.files:
            img = request.files["file"]
            print(img,"  img")
        
            ad=img.filename
            print(ad)

            allowList=[".jpg",".gif",".png"]

            if ad and (ad[-4:].lower() in allowList or ad[-5:].lower()==".jpeg"):
                data = users.query.filter_by(id=session["id"]).first()
            
                
                sonad=str(session["id"])+ad
            
                print(os.path.join("static/image/"))
                img.save(os.path.join("static/image/",sonad))
                image_path="static/image/"+sonad
                os.chdir("static/image")
                if kohne != str(session["id"]):
                    if kohne != "default.png":
                        os.remove(kohne)
                        
                os.chdir("../../")
                data.photo=sonad
                db.session.commit()
                return render_template("profil.html",image_file=image_path,data=data)
            else:
            
                data = users.query.filter_by(id=session["id"]).first()
                data.photo="default.png"
                db.session.commit()
                
                
                image_path="static/image/default.png"
                if kohne!="default.png":
                    os.chdir("static/image")
                    os.remove(kohne)
                    os.chdir("../../")
                flash("Şəkiliniz Güncənlənmədi 'Default' Şekil Qoyuldu","danger")
                return render_template("profil.html",image_file=image_path,data=data)
        
        else:
            
            data = users.query.filter_by(id=session["id"]).first()
            data.photo="default.png"
            db.session.commit()
            
            
            image_path="static/image/default.png"
            if kohne!="default.png":
                os.chdir("static/image")
                os.remove(kohne)
                os.chdir("../../")
            flash("Şəkiliniz Güncənlənmədi 'Default' Şekil Qoyuldu","danger")
            return render_template("profil.html",image_file=image_path,data=data)
    
   


@app.route("/updateProfil",methods=["GET","POST"])
@login_required
def profilUpdate():
    if request.method == "GET":


        data = users.query.filter_by(id=session["id"]).first()


        #Fromun Icini Doldururuq
        form  = updateProfil()
        form.name.data = data.name
        form.username.data = data.username
        form.email.data = data.email
        photo_loc = os.path.join("static/image/",data.photo)

        
        return render_template("updateProfil.html",id=session["id"],form=form,image_file=photo_loc)
    else:
        form2=updateProfil(request.form)
        newName=form2.name.data
        newUsername=form2.username.data
        newEmail=form2.email.data
        newPassword=form2.password.data
        newConfirmPass=form2.confirm.data

        print(newPassword,bool(newPassword)) 
        if bool(newPassword) == False and bool(newConfirmPass) == False:
            print("ife daxil oldu")
            if len(newName)>3 and len(newUsername)>4 and len(newEmail)>7:
                data = users.query.filter_by(id=session["id"]).first()
                data.name=newName
                data.username=newUsername
                data.email=newEmail
                db.session.commit()

                flash("Məlumatlariniz Güncənləndi","success1")
                return redirect(url_for("profil"))
            flash("Xəta Baş Verdi Yenidən Yoxlayın Məlumatlarınız Dəyişilmədi!","danger")
            return redirect(url_for("profil"))          
            

        elif newPassword !=False and newPassword==newConfirmPass and len(newPassword)>4:
            if len(newName)>3 and len(newUsername)>4 and len(newEmail)>7:
                newPassword=sha256_crypt.encrypt(newPassword)
                data = users.query.filter_by(id=session["id"]).first()
                data.name = newName
                data.username = newUsername
                data.email = newEmail
                data.password=newPassword

                db.session.commit()
                flash("Məlumatlariniz Güncənləndi","success1")
                return redirect(url_for("profil"))

            flash("Xəta Baş Verdi Yenidən Yoxlayın Məlumatlarınız Dəyişilmədi!","danger")
            return redirect(url_for("profil"))
        flash("Xəta Baş Verdi Yenidən Yoxlayın Məlumatlarınız Dəyişilmədi!","danger")
        return redirect(url_for("profil"))

@app.route("/viewProfil/<string:id>")
def viewProfil(id):

    data = users.query.filter_by(id=id).first()


    image_loc=data.photo
    return render_template("viewProfil.html",image_file=("static/image/"+image_loc),data=data)


@app.route("/chat",methods=["GET","POST"])
def chat():
    message = chatroom.query.all()
    print(message,message)
    return render_template("chat.html",name=session["username"],message=message)

def messageRecived():
  print( 'message was received!!!' )

@socketio.on( 'my event' )
def handle_my_custom_event( json ):
  print( 'recived my event: ' + str( json ) )
  if "message" in json:
    print(json["message"],"js")

    newMessage=chatroom(name=session["username"],message=json["message"])
    db.session.add(newMessage)
    db.session.commit()
  socketio.emit( 'my response', json, callback=messageRecived )



@app.route("/addComment/<string:id>",methods=["POST"])
@login_required
def addComment(id):
    print(id)
    return redirect("/articles/"+str(id))



if __name__ == "__main__":
    db.create_all()
    socketio.run( app, debug = True )
    #app.run(debug=True)    
   # app.run(host='0.0.0.0')
