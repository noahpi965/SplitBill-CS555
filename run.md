http://localhost:3000/

cd /Users/pitianyi/PycharmProjects/SplitBill-CS555/backend
source venv/bin/activate
python app.py




cd /Users/pitianyi/PycharmProjects/SplitBill-CS555/frontend
npm run dev
jcl


lsof -ti :3000 -ti :5001 | xargs kill

cd /Users/pitianyi/PycharmProjects/SplitBill-CS555/backend
source venv/bin/activate
pytest tests/ -v