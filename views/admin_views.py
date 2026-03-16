from flask import jsonify
from models.mongodb import get_collection
from utils.api.jwt_utils import admin_required

@admin_required
def admin_stats_view():
    users_coll = get_collection("users")
    usage_coll = get_collection("usage_counters")
    
    # 2. Statistiques globales
    total_users = users_coll.count_documents({})
    
    pipeline = [
        {"$match": {"feature": "rag_query"}},
        {"$group": {"_id": None, "total": {"$sum": "$count"}}}
    ]
    reqs_agg = list(usage_coll.aggregate(pipeline))
    total_chat_requests = reqs_agg[0]["total"] if reqs_agg else 0
    
    # 3. Liste des utilisateurs récents (Vue détaillé réquise par le client)
    recent_users_cursor = users_coll.find({}, {"email": 1, "created_at": 1, "email_verified": 1, "_id": 0}).sort("created_at", -1).limit(50)
    users_list = []
    for u in recent_users_cursor:
        users_list.append({
            "email": u.get("email"),
            "created_at": u.get("created_at").strftime("%Y-%m-%d %H:%M") if u.get("created_at") else "N/A"
        })
    
    return jsonify({
        "ok": True,
        "stats": {
            "total_users": total_users,
            "total_chat_requests": total_chat_requests,
            "recent_users": users_list
        }
    })
