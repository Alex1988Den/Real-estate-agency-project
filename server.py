from fastapi import FastAPI, HTTPException, Depends, status
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import joblib
import pandas as pd
import uvicorn
import threading
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация FastAPI
app = FastAPI()

# Загрузка модели
model = joblib.load('best_lightgbm_model.pkl')

# Настройка OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username == "user" and form_data.password == "password":
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": form_data.username}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.post("/predict/", dependencies=[Depends(verify_token)])
def predict(data: dict):
    try:
        df = preprocess_data(data)
        prediction = model.predict(df)
        logger.info(f"Prediction: {prediction.tolist()}")
        return {"prediction": prediction.tolist()}
    except Exception as e:
        logger.error(f"Error in prediction: {str(e)}")
        raise HTTPException(status_code=500, detail="Prediction error")

def preprocess_data(data):
    required_columns = model.feature_name_
    df = pd.DataFrame([data])
    missing_cols = [col for col in required_columns if col not in df.columns]
    missing_df = pd.DataFrame(0, index=df.index, columns=missing_cols)
    df = pd.concat([df, missing_df], axis=1)
    df = df[required_columns]
    return df

# Настройка мониторинга
Instrumentator().instrument(app).expose(app)

def run_server():
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start() 
