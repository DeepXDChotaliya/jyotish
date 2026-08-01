"""
Offline place lookup. Name in, coordinates and IANA zone out.

Typing latitude by hand is the fastest way to cast a wrong chart, and a whole
degree of longitude moves the lagna by about four minutes of birth time. This
table is weighted to India and Sri Lanka because that is where the birth data
mostly comes from, with world cities behind it.

Every zone here is an IANA identifier, so historical offsets still resolve
through zoneinfo. Nothing is hardcoded to a numeric offset.
"""

from __future__ import annotations

import unicodedata

# name, admin area, country, latitude, longitude, IANA zone
CITIES = [
    # ---- India -----------------------------------------------------------
    ("Mumbai", "Maharashtra", "India", 19.0760, 72.8777, "Asia/Kolkata"),
    ("Delhi", "Delhi", "India", 28.6139, 77.2090, "Asia/Kolkata"),
    ("New Delhi", "Delhi", "India", 28.6139, 77.2090, "Asia/Kolkata"),
    ("Bengaluru", "Karnataka", "India", 12.9716, 77.5946, "Asia/Kolkata"),
    ("Bangalore", "Karnataka", "India", 12.9716, 77.5946, "Asia/Kolkata"),
    ("Hyderabad", "Telangana", "India", 17.3850, 78.4867, "Asia/Kolkata"),
    ("Chennai", "Tamil Nadu", "India", 13.0827, 80.2707, "Asia/Kolkata"),
    ("Kolkata", "West Bengal", "India", 22.5726, 88.3639, "Asia/Kolkata"),
    ("Pune", "Maharashtra", "India", 18.5204, 73.8567, "Asia/Kolkata"),
    ("Ahmedabad", "Gujarat", "India", 23.0225, 72.5714, "Asia/Kolkata"),
    ("Surat", "Gujarat", "India", 21.1702, 72.8311, "Asia/Kolkata"),
    ("Jaipur", "Rajasthan", "India", 26.9124, 75.7873, "Asia/Kolkata"),
    ("Lucknow", "Uttar Pradesh", "India", 26.8467, 80.9462, "Asia/Kolkata"),
    ("Kanpur", "Uttar Pradesh", "India", 26.4499, 80.3319, "Asia/Kolkata"),
    ("Nagpur", "Maharashtra", "India", 21.1458, 79.0882, "Asia/Kolkata"),
    ("Indore", "Madhya Pradesh", "India", 22.7196, 75.8577, "Asia/Kolkata"),
    ("Bhopal", "Madhya Pradesh", "India", 23.2599, 77.4126, "Asia/Kolkata"),
    ("Patna", "Bihar", "India", 25.5941, 85.1376, "Asia/Kolkata"),
    ("Vadodara", "Gujarat", "India", 22.3072, 73.1812, "Asia/Kolkata"),
    ("Ludhiana", "Punjab", "India", 30.9010, 75.8573, "Asia/Kolkata"),
    ("Agra", "Uttar Pradesh", "India", 27.1767, 78.0081, "Asia/Kolkata"),
    ("Nashik", "Maharashtra", "India", 19.9975, 73.7898, "Asia/Kolkata"),
    ("Varanasi", "Uttar Pradesh", "India", 25.3176, 82.9739, "Asia/Kolkata"),
    ("Srinagar", "Jammu and Kashmir", "India", 34.0837, 74.7973, "Asia/Kolkata"),
    ("Amritsar", "Punjab", "India", 31.6340, 74.8723, "Asia/Kolkata"),
    ("Chandigarh", "Chandigarh", "India", 30.7333, 76.7794, "Asia/Kolkata"),
    ("Coimbatore", "Tamil Nadu", "India", 11.0168, 76.9558, "Asia/Kolkata"),
    ("Madurai", "Tamil Nadu", "India", 9.9252, 78.1198, "Asia/Kolkata"),
    ("Kochi", "Kerala", "India", 9.9312, 76.2673, "Asia/Kolkata"),
    ("Thiruvananthapuram", "Kerala", "India", 8.5241, 76.9366, "Asia/Kolkata"),
    ("Kozhikode", "Kerala", "India", 11.2588, 75.7804, "Asia/Kolkata"),
    ("Thrissur", "Kerala", "India", 10.5276, 76.2144, "Asia/Kolkata"),
    ("Mysuru", "Karnataka", "India", 12.2958, 76.6394, "Asia/Kolkata"),
    ("Mangaluru", "Karnataka", "India", 12.9141, 74.8560, "Asia/Kolkata"),
    ("Hubli", "Karnataka", "India", 15.3647, 75.1240, "Asia/Kolkata"),
    ("Visakhapatnam", "Andhra Pradesh", "India", 17.6868, 83.2185, "Asia/Kolkata"),
    ("Vijayawada", "Andhra Pradesh", "India", 16.5062, 80.6480, "Asia/Kolkata"),
    ("Tirupati", "Andhra Pradesh", "India", 13.6288, 79.4192, "Asia/Kolkata"),
    ("Bhubaneswar", "Odisha", "India", 20.2961, 85.8245, "Asia/Kolkata"),
    ("Cuttack", "Odisha", "India", 20.4625, 85.8830, "Asia/Kolkata"),
    ("Guwahati", "Assam", "India", 26.1445, 91.7362, "Asia/Kolkata"),
    ("Ranchi", "Jharkhand", "India", 23.3441, 85.3096, "Asia/Kolkata"),
    ("Raipur", "Chhattisgarh", "India", 21.2514, 81.6296, "Asia/Kolkata"),
    ("Dehradun", "Uttarakhand", "India", 30.3165, 78.0322, "Asia/Kolkata"),
    ("Rishikesh", "Uttarakhand", "India", 30.0869, 78.2676, "Asia/Kolkata"),
    ("Haridwar", "Uttarakhand", "India", 29.9457, 78.1642, "Asia/Kolkata"),
    ("Shimla", "Himachal Pradesh", "India", 31.1048, 77.1734, "Asia/Kolkata"),
    ("Dharamshala", "Himachal Pradesh", "India", 32.2190, 76.3234, "Asia/Kolkata"),
    ("Jodhpur", "Rajasthan", "India", 26.2389, 73.0243, "Asia/Kolkata"),
    ("Udaipur", "Rajasthan", "India", 24.5854, 73.7125, "Asia/Kolkata"),
    ("Ajmer", "Rajasthan", "India", 26.4499, 74.6399, "Asia/Kolkata"),
    ("Gwalior", "Madhya Pradesh", "India", 26.2183, 78.1828, "Asia/Kolkata"),
    ("Jabalpur", "Madhya Pradesh", "India", 23.1815, 79.9864, "Asia/Kolkata"),
    ("Ujjain", "Madhya Pradesh", "India", 23.1765, 75.7885, "Asia/Kolkata"),
    ("Allahabad", "Uttar Pradesh", "India", 25.4358, 81.8463, "Asia/Kolkata"),
    ("Prayagraj", "Uttar Pradesh", "India", 25.4358, 81.8463, "Asia/Kolkata"),
    ("Meerut", "Uttar Pradesh", "India", 28.9845, 77.7064, "Asia/Kolkata"),
    ("Noida", "Uttar Pradesh", "India", 28.5355, 77.3910, "Asia/Kolkata"),
    ("Gurugram", "Haryana", "India", 28.4595, 77.0266, "Asia/Kolkata"),
    ("Faridabad", "Haryana", "India", 28.4089, 77.3178, "Asia/Kolkata"),
    ("Jalandhar", "Punjab", "India", 31.3260, 75.5762, "Asia/Kolkata"),
    ("Jammu", "Jammu and Kashmir", "India", 32.7266, 74.8570, "Asia/Kolkata"),
    ("Aurangabad", "Maharashtra", "India", 19.8762, 75.3433, "Asia/Kolkata"),
    ("Kolhapur", "Maharashtra", "India", 16.7050, 74.2433, "Asia/Kolkata"),
    ("Solapur", "Maharashtra", "India", 17.6599, 75.9064, "Asia/Kolkata"),
    ("Thane", "Maharashtra", "India", 19.2183, 72.9781, "Asia/Kolkata"),
    ("Navi Mumbai", "Maharashtra", "India", 19.0330, 73.0297, "Asia/Kolkata"),
    ("Panaji", "Goa", "India", 15.4909, 73.8278, "Asia/Kolkata"),
    ("Margao", "Goa", "India", 15.2832, 73.9862, "Asia/Kolkata"),
    ("Mapusa", "Goa", "India", 15.5937, 73.8142, "Asia/Kolkata"),
    ("Vasco da Gama", "Goa", "India", 15.3860, 73.8157, "Asia/Kolkata"),
    ("Arambol", "Goa", "India", 15.6869, 73.7043, "Asia/Kolkata"),
    ("Mandrem", "Goa", "India", 15.6650, 73.7180, "Asia/Kolkata"),
    ("Anjuna", "Goa", "India", 15.5752, 73.7401, "Asia/Kolkata"),
    ("Gokarna", "Karnataka", "India", 14.5479, 74.3188, "Asia/Kolkata"),
    ("Puducherry", "Puducherry", "India", 11.9416, 79.8083, "Asia/Kolkata"),
    ("Tiruchirappalli", "Tamil Nadu", "India", 10.7905, 78.7047, "Asia/Kolkata"),
    ("Salem", "Tamil Nadu", "India", 11.6643, 78.1460, "Asia/Kolkata"),
    ("Vellore", "Tamil Nadu", "India", 12.9165, 79.1325, "Asia/Kolkata"),
    ("Siliguri", "West Bengal", "India", 26.7271, 88.3953, "Asia/Kolkata"),
    ("Darjeeling", "West Bengal", "India", 27.0360, 88.2627, "Asia/Kolkata"),
    ("Howrah", "West Bengal", "India", 22.5958, 88.2636, "Asia/Kolkata"),
    ("Imphal", "Manipur", "India", 24.8170, 93.9368, "Asia/Kolkata"),
    ("Shillong", "Meghalaya", "India", 25.5788, 91.8933, "Asia/Kolkata"),
    ("Aizawl", "Mizoram", "India", 23.7271, 92.7176, "Asia/Kolkata"),
    ("Itanagar", "Arunachal Pradesh", "India", 27.0844, 93.6053, "Asia/Kolkata"),
    ("Gangtok", "Sikkim", "India", 27.3389, 88.6065, "Asia/Kolkata"),
    ("Agartala", "Tripura", "India", 23.8315, 91.2868, "Asia/Kolkata"),
    ("Kohima", "Nagaland", "India", 25.6751, 94.1086, "Asia/Kolkata"),
    ("Dispur", "Assam", "India", 26.1433, 91.7898, "Asia/Kolkata"),
    ("Leh", "Ladakh", "India", 34.1526, 77.5771, "Asia/Kolkata"),
    ("Port Blair", "Andaman and Nicobar", "India", 11.6234, 92.7265, "Asia/Kolkata"),

    # ---- Sri Lanka -------------------------------------------------------
    ("Colombo", "Western", "Sri Lanka", 6.9271, 79.8612, "Asia/Colombo"),
    ("Kandy", "Central", "Sri Lanka", 7.2906, 80.6337, "Asia/Colombo"),
    ("Galle", "Southern", "Sri Lanka", 6.0535, 80.2210, "Asia/Colombo"),
    ("Jaffna", "Northern", "Sri Lanka", 9.6615, 80.0255, "Asia/Colombo"),
    ("Negombo", "Western", "Sri Lanka", 7.2083, 79.8358, "Asia/Colombo"),
    ("Matara", "Southern", "Sri Lanka", 5.9549, 80.5550, "Asia/Colombo"),
    ("Anuradhapura", "North Central", "Sri Lanka", 8.3114, 80.4037, "Asia/Colombo"),
    ("Trincomalee", "Eastern", "Sri Lanka", 8.5874, 81.2152, "Asia/Colombo"),
    ("Batticaloa", "Eastern", "Sri Lanka", 7.7102, 81.6924, "Asia/Colombo"),
    ("Nuwara Eliya", "Central", "Sri Lanka", 6.9497, 80.7891, "Asia/Colombo"),
    ("Ratnapura", "Sabaragamuwa", "Sri Lanka", 6.6828, 80.3992, "Asia/Colombo"),
    ("Kurunegala", "North Western", "Sri Lanka", 7.4863, 80.3647, "Asia/Colombo"),
    ("Badulla", "Uva", "Sri Lanka", 6.9934, 81.0550, "Asia/Colombo"),
    ("Sri Jayawardenepura Kotte", "Western", "Sri Lanka", 6.8880, 79.9187, "Asia/Colombo"),

    # ---- South and Southeast Asia ---------------------------------------
    ("Kathmandu", "Bagmati", "Nepal", 27.7172, 85.3240, "Asia/Kathmandu"),
    ("Pokhara", "Gandaki", "Nepal", 28.2096, 83.9856, "Asia/Kathmandu"),
    ("Dhaka", "Dhaka", "Bangladesh", 23.8103, 90.4125, "Asia/Dhaka"),
    ("Chittagong", "Chittagong", "Bangladesh", 22.3569, 91.7832, "Asia/Dhaka"),
    ("Karachi", "Sindh", "Pakistan", 24.8607, 67.0011, "Asia/Karachi"),
    ("Lahore", "Punjab", "Pakistan", 31.5204, 74.3587, "Asia/Karachi"),
    ("Islamabad", "Islamabad", "Pakistan", 33.6844, 73.0479, "Asia/Karachi"),
    ("Thimphu", "Thimphu", "Bhutan", 27.4728, 89.6390, "Asia/Thimphu"),
    ("Malé", "Malé", "Maldives", 4.1755, 73.5093, "Indian/Maldives"),
    ("Kabul", "Kabul", "Afghanistan", 34.5553, 69.2075, "Asia/Kabul"),
    ("Bangkok", "Bangkok", "Thailand", 13.7563, 100.5018, "Asia/Bangkok"),
    ("Chiang Mai", "Chiang Mai", "Thailand", 18.7883, 98.9853, "Asia/Bangkok"),
    ("Singapore", "", "Singapore", 1.3521, 103.8198, "Asia/Singapore"),
    ("Kuala Lumpur", "", "Malaysia", 3.1390, 101.6869, "Asia/Kuala_Lumpur"),
    ("Jakarta", "Jakarta", "Indonesia", -6.2088, 106.8456, "Asia/Jakarta"),
    ("Denpasar", "Bali", "Indonesia", -8.6705, 115.2126, "Asia/Makassar"),
    ("Ubud", "Bali", "Indonesia", -8.5069, 115.2625, "Asia/Makassar"),
    ("Manila", "Metro Manila", "Philippines", 14.5995, 120.9842, "Asia/Manila"),
    ("Hanoi", "Hanoi", "Vietnam", 21.0278, 105.8342, "Asia/Ho_Chi_Minh"),
    ("Ho Chi Minh City", "", "Vietnam", 10.8231, 106.6297, "Asia/Ho_Chi_Minh"),
    ("Yangon", "Yangon", "Myanmar", 16.8661, 96.1951, "Asia/Yangon"),
    ("Phnom Penh", "", "Cambodia", 11.5564, 104.9282, "Asia/Phnom_Penh"),

    # ---- East Asia -------------------------------------------------------
    ("Tokyo", "Tokyo", "Japan", 35.6762, 139.6503, "Asia/Tokyo"),
    ("Osaka", "Osaka", "Japan", 34.6937, 135.5023, "Asia/Tokyo"),
    ("Kyoto", "Kyoto", "Japan", 35.0116, 135.7681, "Asia/Tokyo"),
    ("Seoul", "Seoul", "South Korea", 37.5665, 126.9780, "Asia/Seoul"),
    ("Beijing", "Beijing", "China", 39.9042, 116.4074, "Asia/Shanghai"),
    ("Shanghai", "Shanghai", "China", 31.2304, 121.4737, "Asia/Shanghai"),
    ("Hong Kong", "", "China", 22.3193, 114.1694, "Asia/Hong_Kong"),
    ("Taipei", "", "Taiwan", 25.0330, 121.5654, "Asia/Taipei"),

    # ---- Middle East -----------------------------------------------------
    ("Dubai", "Dubai", "United Arab Emirates", 25.2048, 55.2708, "Asia/Dubai"),
    ("Abu Dhabi", "Abu Dhabi", "United Arab Emirates", 24.4539, 54.3773, "Asia/Dubai"),
    ("Doha", "", "Qatar", 25.2854, 51.5310, "Asia/Qatar"),
    ("Muscat", "", "Oman", 23.5880, 58.3829, "Asia/Muscat"),
    ("Riyadh", "Riyadh", "Saudi Arabia", 24.7136, 46.6753, "Asia/Riyadh"),
    ("Jeddah", "Makkah", "Saudi Arabia", 21.4858, 39.1925, "Asia/Riyadh"),
    ("Kuwait City", "", "Kuwait", 29.3759, 47.9774, "Asia/Kuwait"),
    ("Manama", "", "Bahrain", 26.2285, 50.5860, "Asia/Bahrain"),
    ("Tehran", "Tehran", "Iran", 35.6892, 51.3890, "Asia/Tehran"),
    ("Tel Aviv", "", "Israel", 32.0853, 34.7818, "Asia/Jerusalem"),
    ("Jerusalem", "", "Israel", 31.7683, 35.2137, "Asia/Jerusalem"),
    ("Istanbul", "Istanbul", "Turkey", 41.0082, 28.9784, "Europe/Istanbul"),
    ("Ankara", "Ankara", "Turkey", 39.9334, 32.8597, "Europe/Istanbul"),

    # ---- Europe ----------------------------------------------------------
    ("London", "England", "United Kingdom", 51.5074, -0.1278, "Europe/London"),
    ("Manchester", "England", "United Kingdom", 53.4808, -2.2426, "Europe/London"),
    ("Birmingham", "England", "United Kingdom", 52.4862, -1.8904, "Europe/London"),
    ("Edinburgh", "Scotland", "United Kingdom", 55.9533, -3.1883, "Europe/London"),
    ("Dublin", "", "Ireland", 53.3498, -6.2603, "Europe/Dublin"),
    ("Paris", "Île-de-France", "France", 48.8566, 2.3522, "Europe/Paris"),
    ("Lyon", "", "France", 45.7640, 4.8357, "Europe/Paris"),
    ("Marseille", "", "France", 43.2965, 5.3698, "Europe/Paris"),
    ("Berlin", "Berlin", "Germany", 52.5200, 13.4050, "Europe/Berlin"),
    ("Munich", "Bavaria", "Germany", 48.1351, 11.5820, "Europe/Berlin"),
    ("Frankfurt", "Hesse", "Germany", 50.1109, 8.6821, "Europe/Berlin"),
    ("Hamburg", "Hamburg", "Germany", 53.5511, 9.9937, "Europe/Berlin"),
    ("Amsterdam", "", "Netherlands", 52.3676, 4.9041, "Europe/Amsterdam"),
    ("Brussels", "", "Belgium", 50.8503, 4.3517, "Europe/Brussels"),
    ("Zurich", "", "Switzerland", 47.3769, 8.5417, "Europe/Zurich"),
    ("Geneva", "", "Switzerland", 46.2044, 6.1432, "Europe/Zurich"),
    ("Vienna", "", "Austria", 48.2082, 16.3738, "Europe/Vienna"),
    ("Rome", "Lazio", "Italy", 41.9028, 12.4964, "Europe/Rome"),
    ("Milan", "Lombardy", "Italy", 45.4642, 9.1900, "Europe/Rome"),
    ("Madrid", "", "Spain", 40.4168, -3.7038, "Europe/Madrid"),
    ("Barcelona", "Catalonia", "Spain", 41.3851, 2.1734, "Europe/Madrid"),
    ("Lisbon", "", "Portugal", 38.7223, -9.1393, "Europe/Lisbon"),
    ("Athens", "", "Greece", 37.9838, 23.7275, "Europe/Athens"),
    ("Stockholm", "", "Sweden", 59.3293, 18.0686, "Europe/Stockholm"),
    ("Oslo", "", "Norway", 59.9139, 10.7522, "Europe/Oslo"),
    ("Copenhagen", "", "Denmark", 55.6761, 12.5683, "Europe/Copenhagen"),
    ("Helsinki", "", "Finland", 60.1699, 24.9384, "Europe/Helsinki"),
    ("Warsaw", "", "Poland", 52.2297, 21.0122, "Europe/Warsaw"),
    ("Prague", "", "Czechia", 50.0755, 14.4378, "Europe/Prague"),
    ("Budapest", "", "Hungary", 47.4979, 19.0402, "Europe/Budapest"),
    ("Bucharest", "", "Romania", 44.4268, 26.1025, "Europe/Bucharest"),
    ("Moscow", "", "Russia", 55.7558, 37.6173, "Europe/Moscow"),
    ("Saint Petersburg", "", "Russia", 59.9311, 30.3609, "Europe/Moscow"),
    ("Kyiv", "", "Ukraine", 50.4501, 30.5234, "Europe/Kyiv"),

    # ---- Africa ----------------------------------------------------------
    ("Cairo", "", "Egypt", 30.0444, 31.2357, "Africa/Cairo"),
    ("Nairobi", "", "Kenya", -1.2921, 36.8219, "Africa/Nairobi"),
    ("Lagos", "Lagos", "Nigeria", 6.5244, 3.3792, "Africa/Lagos"),
    ("Accra", "", "Ghana", 5.6037, -0.1870, "Africa/Accra"),
    ("Johannesburg", "Gauteng", "South Africa", -26.2041, 28.0473, "Africa/Johannesburg"),
    ("Cape Town", "Western Cape", "South Africa", -33.9249, 18.4241, "Africa/Johannesburg"),
    ("Durban", "KwaZulu-Natal", "South Africa", -29.8587, 31.0218, "Africa/Johannesburg"),
    ("Addis Ababa", "", "Ethiopia", 9.0320, 38.7469, "Africa/Addis_Ababa"),
    ("Dar es Salaam", "", "Tanzania", -6.7924, 39.2083, "Africa/Dar_es_Salaam"),
    ("Kampala", "", "Uganda", 0.3476, 32.5825, "Africa/Kampala"),
    ("Casablanca", "", "Morocco", 33.5731, -7.5898, "Africa/Casablanca"),
    ("Port Louis", "", "Mauritius", -20.1609, 57.5012, "Indian/Mauritius"),

    # ---- Americas --------------------------------------------------------
    ("New York", "New York", "United States", 40.7128, -74.0060, "America/New_York"),
    ("Boston", "Massachusetts", "United States", 42.3601, -71.0589, "America/New_York"),
    ("Washington", "DC", "United States", 38.9072, -77.0369, "America/New_York"),
    ("Atlanta", "Georgia", "United States", 33.7490, -84.3880, "America/New_York"),
    ("Miami", "Florida", "United States", 25.7617, -80.1918, "America/New_York"),
    ("Chicago", "Illinois", "United States", 41.8781, -87.6298, "America/Chicago"),
    ("Houston", "Texas", "United States", 29.7604, -95.3698, "America/Chicago"),
    ("Dallas", "Texas", "United States", 32.7767, -96.7970, "America/Chicago"),
    ("Austin", "Texas", "United States", 30.2672, -97.7431, "America/Chicago"),
    ("Denver", "Colorado", "United States", 39.7392, -104.9903, "America/Denver"),
    ("Phoenix", "Arizona", "United States", 33.4484, -112.0740, "America/Phoenix"),
    ("Los Angeles", "California", "United States", 34.0522, -118.2437, "America/Los_Angeles"),
    ("San Francisco", "California", "United States", 37.7749, -122.4194, "America/Los_Angeles"),
    ("San Jose", "California", "United States", 37.3382, -121.8863, "America/Los_Angeles"),
    ("Seattle", "Washington", "United States", 47.6062, -122.3321, "America/Los_Angeles"),
    ("Honolulu", "Hawaii", "United States", 21.3069, -157.8583, "Pacific/Honolulu"),
    ("Toronto", "Ontario", "Canada", 43.6532, -79.3832, "America/Toronto"),
    ("Montreal", "Quebec", "Canada", 45.5017, -73.5673, "America/Toronto"),
    ("Vancouver", "British Columbia", "Canada", 49.2827, -123.1207, "America/Vancouver"),
    ("Calgary", "Alberta", "Canada", 51.0447, -114.0719, "America/Edmonton"),
    ("Mexico City", "", "Mexico", 19.4326, -99.1332, "America/Mexico_City"),
    ("Bogotá", "", "Colombia", 4.7110, -74.0721, "America/Bogota"),
    ("Lima", "", "Peru", -12.0464, -77.0428, "America/Lima"),
    ("Santiago", "", "Chile", -33.4489, -70.6693, "America/Santiago"),
    ("Buenos Aires", "", "Argentina", -34.6037, -58.3816, "America/Argentina/Buenos_Aires"),
    ("São Paulo", "", "Brazil", -23.5505, -46.6333, "America/Sao_Paulo"),
    ("Rio de Janeiro", "", "Brazil", -22.9068, -43.1729, "America/Sao_Paulo"),
    ("Port of Spain", "", "Trinidad and Tobago", 10.6596, -61.5019, "America/Port_of_Spain"),
    ("Georgetown", "", "Guyana", 6.8013, -58.1553, "America/Guyana"),
    ("Paramaribo", "", "Suriname", 5.8520, -55.2038, "America/Paramaribo"),
    ("Kingston", "", "Jamaica", 17.9714, -76.7936, "America/Jamaica"),

    # ---- Northern and remaining Europe -----------------------------------
    ("Reykjavik", "", "Iceland", 64.1466, -21.9426, "Atlantic/Reykjavik"),
    ("Tallinn", "", "Estonia", 59.4370, 24.7536, "Europe/Tallinn"),
    ("Riga", "", "Latvia", 56.9496, 24.1052, "Europe/Riga"),
    ("Vilnius", "", "Lithuania", 54.6872, 25.2797, "Europe/Vilnius"),
    ("Minsk", "", "Belarus", 53.9006, 27.5590, "Europe/Minsk"),
    ("Belgrade", "", "Serbia", 44.7866, 20.4489, "Europe/Belgrade"),
    ("Zagreb", "", "Croatia", 45.8150, 15.9819, "Europe/Zagreb"),
    ("Sofia", "", "Bulgaria", 42.6977, 23.3219, "Europe/Sofia"),
    ("Bratislava", "", "Slovakia", 48.1486, 17.1077, "Europe/Bratislava"),
    ("Ljubljana", "", "Slovenia", 46.0569, 14.5058, "Europe/Ljubljana"),
    ("Luxembourg", "", "Luxembourg", 49.6116, 6.1319, "Europe/Luxembourg"),
    ("Valletta", "", "Malta", 35.8989, 14.5146, "Europe/Malta"),
    ("Nicosia", "", "Cyprus", 35.1856, 33.3823, "Asia/Nicosia"),
    ("Tbilisi", "", "Georgia", 41.7151, 44.8271, "Asia/Tbilisi"),
    ("Yerevan", "", "Armenia", 40.1792, 44.4991, "Asia/Yerevan"),
    ("Baku", "", "Azerbaijan", 40.4093, 49.8671, "Asia/Baku"),
    ("Tashkent", "", "Uzbekistan", 41.2995, 69.2401, "Asia/Tashkent"),
    ("Almaty", "", "Kazakhstan", 43.2220, 76.8512, "Asia/Almaty"),

    # ---- More Americas and Africa ----------------------------------------
    ("Havana", "", "Cuba", 23.1136, -82.3666, "America/Havana"),
    ("Panama City", "", "Panama", 8.9824, -79.5199, "America/Panama"),
    ("San Juan", "", "Puerto Rico", 18.4655, -66.1057, "America/Puerto_Rico"),
    ("Quito", "", "Ecuador", -0.1807, -78.4678, "America/Guayaquil"),
    ("La Paz", "", "Bolivia", -16.4897, -68.1193, "America/La_Paz"),
    ("Montevideo", "", "Uruguay", -34.9011, -56.1645, "America/Montevideo"),
    ("Asuncion", "", "Paraguay", -25.2637, -57.5759, "America/Asuncion"),
    ("Caracas", "", "Venezuela", 10.4806, -66.9036, "America/Caracas"),
    ("Ottawa", "Ontario", "Canada", 45.4215, -75.6972, "America/Toronto"),
    ("Minneapolis", "Minnesota", "United States", 44.9778, -93.2650, "America/Chicago"),
    ("Detroit", "Michigan", "United States", 42.3314, -83.0458, "America/Detroit"),
    ("Philadelphia", "Pennsylvania", "United States", 39.9526, -75.1652, "America/New_York"),
    ("San Diego", "California", "United States", 32.7157, -117.1611, "America/Los_Angeles"),
    ("Las Vegas", "Nevada", "United States", 36.1699, -115.1398, "America/Los_Angeles"),
    ("Anchorage", "Alaska", "United States", 61.2181, -149.9003, "America/Anchorage"),
    ("Abuja", "", "Nigeria", 9.0765, 7.3986, "Africa/Lagos"),
    ("Dakar", "", "Senegal", 14.7167, -17.4677, "Africa/Dakar"),
    ("Abidjan", "", "Ivory Coast", 5.3600, -4.0083, "Africa/Abidjan"),
    ("Khartoum", "", "Sudan", 15.5007, 32.5599, "Africa/Khartoum"),
    ("Lusaka", "", "Zambia", -15.3875, 28.3228, "Africa/Lusaka"),
    ("Harare", "", "Zimbabwe", -17.8252, 31.0335, "Africa/Harare"),
    ("Maputo", "", "Mozambique", -25.9692, 32.5732, "Africa/Maputo"),
    ("Kigali", "", "Rwanda", -1.9441, 30.0619, "Africa/Kigali"),
    ("Antananarivo", "", "Madagascar", -18.8792, 47.5079, "Indian/Antananarivo"),
    ("Victoria", "", "Seychelles", -4.6191, 55.4513, "Indian/Mahe"),
    ("Tunis", "", "Tunisia", 36.8065, 10.1815, "Africa/Tunis"),
    ("Algiers", "", "Algeria", 36.7538, 3.0588, "Africa/Algiers"),
    ("Marrakesh", "", "Morocco", 31.6295, -7.9811, "Africa/Casablanca"),

    # ---- Oceania ---------------------------------------------------------
    ("Sydney", "New South Wales", "Australia", -33.8688, 151.2093, "Australia/Sydney"),
    ("Melbourne", "Victoria", "Australia", -37.8136, 144.9631, "Australia/Melbourne"),
    ("Brisbane", "Queensland", "Australia", -27.4698, 153.0251, "Australia/Brisbane"),
    ("Perth", "Western Australia", "Australia", -31.9505, 115.8605, "Australia/Perth"),
    ("Adelaide", "South Australia", "Australia", -34.9285, 138.6007, "Australia/Adelaide"),
    ("Canberra", "ACT", "Australia", -35.2809, 149.1300, "Australia/Sydney"),
    ("Auckland", "", "New Zealand", -36.8485, 174.7633, "Pacific/Auckland"),
    ("Wellington", "", "New Zealand", -41.2865, 174.7762, "Pacific/Auckland"),
    ("Suva", "", "Fiji", -18.1248, 178.4501, "Pacific/Fiji"),
]


def _fold(s: str) -> str:
    """Strip accents and case so 'Malé' matches 'male'."""
    return "".join(
        c for c in unicodedata.normalize("NFD", s.lower())
        if unicodedata.category(c) != "Mn"
    )


_INDEX = [(_fold(c[0]), _fold(c[1]), _fold(c[2]), c) for c in CITIES]


def search(query: str, limit: int = 12) -> list[dict]:
    """Ranked lookup over city, state and country.

    Typing a state or a country has to work, because people describe a birth
    place as "somewhere in Goa" far more often than they name the municipality.
    Ordering is exact city, city prefix, city substring, then region and
    country matches.
    """
    q = _fold(query.strip())
    if not q:
        return []

    # A trailing region qualifier is common: "panaji goa" or "kandy sri lanka".
    parts = [p for p in q.replace(",", " ").split() if p]

    exact, prefix, contains, region = [], [], [], []
    for name, admin, country, row in _INDEX:
        haystack = "%s %s %s" % (name, admin, country)
        if name == q:
            exact.append(row)
        elif name.startswith(q):
            prefix.append(row)
        elif q in name:
            contains.append(row)
        elif admin.startswith(q) or country.startswith(q):
            region.append(row)
        elif len(parts) > 1 and all(p in haystack for p in parts):
            contains.append(row)
        elif q in admin or q in country:
            region.append(row)

    ordered = exact + prefix + contains + region
    seen, out = set(), []
    for r in ordered:
        if r[0] in seen:
            continue
        seen.add(r[0])
        out.append(as_dict(r))
        if len(out) >= limit:
            break
    return out


def as_dict(row) -> dict:
    name, admin, country, lat, lon, tz = row
    label = ", ".join(p for p in (name, admin, country) if p)
    return {
        "name": name,
        "admin": admin,
        "country": country,
        "label": label,
        "latitude": lat,
        "longitude": lon,
        "timezone": tz,
    }


def resolve(query: str) -> dict | None:
    """Best single match, or None. Used when a saved chart names a place."""
    hits = search(query, limit=1)
    return hits[0] if hits else None


def dump_json() -> str:
    """The city table as compact JSON for the browser.

    The UI searches this locally rather than calling the API on every
    keystroke. That keeps the location field working when the Python backend
    is unreachable, which is the difference between a form a person can fill
    in and a form that silently does nothing.
    """
    import json
    return json.dumps(
        [{"n": c[0], "a": c[1], "c": c[2], "la": c[3], "lo": c[4], "tz": c[5]}
         for c in CITIES], separators=(",", ":"), ensure_ascii=False)


if __name__ == "__main__":
    import pathlib
    target = pathlib.Path(__file__).resolve().parent.parent / "ui" / "cities.json"
    target.write_text(dump_json(), encoding="utf-8")
    print("wrote %s (%d cities, %.1f KB)" % (
        target, len(CITIES), len(target.read_bytes()) / 1024))
