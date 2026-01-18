# Air Quality Dashboard :sparkles:

Dashboard ini dibuat untuk menganalisis data kualitas udara di stasiun Changping, Dingling, dan Dongsi (Beijing). Dashboard ini menyajikan visualisasi tren harian, pola musiman, korelasi antar variabel cuaca, dan pengaruh curah hujan terhadap tingkat polusi.

## Setup Environment - Anaconda

Jika Anda menggunakan Anaconda, ikuti langkah berikut untuk membuat environment baru:

```
conda create --name main-ds python=3.13.9
conda activate main-ds
pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal
```
mkdir proyek_analisis_data
cd proyek_analisis_data
pipenv install
pipenv shell
pip install -r requirements.txt
```

## Run steamlit app
```
streamlit run dashboard.py
```