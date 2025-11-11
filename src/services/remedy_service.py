# src/services/remedy_service.py

# Multi-religion remedy database
REMEDIES = {
    "hindu": {
        "Career": (
            "Recite the 'Hanuman Chalisa' on Tuesdays and avoid wearing black on Saturdays. "
            "Chant 'Om Vigneshwaraya Namaha' daily to remove obstacles. "
            "Offer mustard seeds to Surya for 41 days. "
            "Donate sweets in copper vessels on Sundays for stability."
        ),
        "Health": (
            "Offer water to the Sun every morning and chant the Maha Mrityunjaya Mantra 108 times daily. "
            "Donate red clothes on Tuesdays, offer milk to Shivling on Mondays. "
            "Install Surya Yantra at home. Wear Rudraksha beads for healing energy."
        ),
        "Marriage": (
            "Fast on Fridays, wear a diamond or opal (if astrologically suitable), and perform Lakshmi puja. "
            "Worship Lord Shiva and Parvati together. Offer white flowers on Fridays. "
            "Chant 'Om Shukraya Namaha' for harmony in relationships."
        ),
        "Finance": (
            "Feed cows on Fridays, offer red lentils to Hanuman temple, and donate on Amavasya. "
            "Place Sri Yantra in your home temple. "
            "Chant 'Om Shreem Mahalakshmiyei Namaha' daily and fast on Thursdays for wealth. "
            "Donate black lentils on Saturdays."
        ),
        "Education": (
            "Chant Saraswati Vandana before studying and wear yellow on Thursdays. "
            "Offer sweets to Goddess Saraswati on study days. "
            "Use Saraswati Yantra and keep your study space in the northeast direction."
        ),
        "Relationships": (
            "Light a ghee lamp in the South-East direction and offer pink flowers to Radha-Krishna. "
            "Chant 'Om Shree Krishnaya Namaha' for emotional bonding. "
            "Do joint charity with your partner to enhance compatibility."
        ),
        "Travel": (
            "Chant Hanuman Chalisa before travel and keep a copper coin in your wallet. "
            "Carry a charged lime with cloves while traveling. "
            "Avoid starting journeys during Rahu Kaal."
        ),
        "Spirituality": (
            "Chant Gayatri Mantra and meditate during Brahma Muhurta daily. "
            "Perform daily japa with Rudraksha mala. "
            "Place a Sri Yantra in your meditation area and practice silence (mauna) weekly."
        ),
        "Property": (
            "Offer milk to Shivling on Mondays and donate bricks at a temple site. "
            "Place Hanuman or Vastu Yantra near the entrance of the house. "
            "Keep Tulsi plant in northeast for spiritual and property stability."
        ),
        "Legal": (
            "Light mustard oil lamp under a Peepal tree on Saturdays and recite Shani Mantra. "
            "Donate black sesame seeds on Saturdays. "
            "Chant 'Om Sham Shanicharaya Namaha' 108 times for legal issues."
        ),
        "General": (
            "Keep a clean space, maintain spiritual routine, and avoid speaking harshly. "
            "Perform regular charity to remove obstacles. "
            "Avoid cutting nails or hair on Tuesdays and Saturdays for energy balance."
        ),
    },
    "christian": {
        "Career": (
            "Pray to St. Joseph, patron saint of workers, for guidance in your career. "
            "Attend Sunday Mass regularly and offer your work to God through prayer. "
            "Practice the Prayer of Jabez for expansion and blessing. "
            "Consider fasting on Fridays and donate to those in need."
        ),
        "Health": (
            "Pray to St. Raphael the Archangel for healing. "
            "Attend healing Masses and receive the Sacrament of Anointing of the Sick if needed. "
            "Use blessed oil and holy water. "
            "Pray the Rosary daily for physical and spiritual healing."
        ),
        "Marriage": (
            "Pray to the Holy Family for marital harmony. "
            "Attend Mass together and pray the Our Father daily. "
            "Read Ephesians 5:21-33 and Corinthians 13 regularly. "
            "Consider marriage counseling through your church and attend marriage retreats."
        ),
        "Finance": (
            "Practice tithing (giving 10% to church and charity). "
            "Pray to St. Matthew, patron saint of finances. "
            "Read Proverbs for wisdom in financial matters. "
            "Trust in God's providence and practice gratitude through prayer."
        ),
        "Education": (
            "Pray to St. Thomas Aquinas, patron saint of students. "
            "Begin study sessions with prayer asking for wisdom. "
            "Read James 1:5 for divine wisdom. "
            "Create a peaceful study environment with a Bible or cross present."
        ),
        "Relationships": (
            "Pray for guidance through the Holy Spirit. "
            "Practice forgiveness as taught by Jesus (Matthew 6:14-15). "
            "Attend church fellowship activities to strengthen community bonds. "
            "Study 1 Corinthians 13 on love and apply its teachings."
        ),
        "Travel": (
            "Pray to St. Christopher, patron saint of travelers, before journeys. "
            "Carry a blessed medal or crucifix during travel. "
            "Recite Psalm 121 for protection. "
            "Ask for your priest's blessing before major trips."
        ),
        "Spirituality": (
            "Attend daily Mass and practice Eucharistic adoration. "
            "Pray the Liturgy of the Hours and read Scripture daily. "
            "Practice Lectio Divina (sacred reading). "
            "Consider spiritual direction and regular confession."
        ),
        "Property": (
            "Have your home blessed by a priest. "
            "Pray to St. Joseph for protection of your dwelling. "
            "Place holy water at entrances and a crucifix in each room. "
            "Practice hospitality as taught in Hebrews 13:2."
        ),
        "Legal": (
            "Pray to St. Ivo, patron saint of lawyers. "
            "Attend Mass and pray for justice and truth. "
            "Fast and ask for your church community's prayers. "
            "Trust in God's justice (Romans 12:19) and seek wise counsel."
        ),
        "General": (
            "Maintain a daily prayer life and attend church regularly. "
            "Practice charity, patience, and kindness. "
            "Read the Bible daily and trust in God's plan. "
            "Participate in sacraments and Christian fellowship."
        ),
    },
    "muslim": {
        "Career": (
            "Pray Salat al-Hajah (Prayer of Need) for career guidance. "
            "Recite Surah Al-Waqiah daily for sustenance. "
            "Give Sadaqah (charity) regularly and help others. "
            "Say 'Bismillah' before starting work and maintain halal practices."
        ),
        "Health": (
            "Recite Ayat al-Kursi and the last two verses of Surah Al-Baqarah. "
            "Read Surah Al-Fatihah as Ruqyah for healing. "
            "Use black seed (Nigella sativa) and honey as prophetic medicine. "
            "Pray Tahajjud and make du'a for shifa (healing)."
        ),
        "Marriage": (
            "Pray Salat al-Istikhara before making marriage decisions. "
            "Recite Surah Ar-Rum verse 21 for marital harmony. "
            "Give charity together and pray together regularly. "
            "Follow the Sunnah in treating your spouse with kindness and respect."
        ),
        "Finance": (
            "Give Zakat regularly and help the poor. "
            "Recite Surah Al-Waqiah after Fajr or Maghrib. "
            "Avoid riba (interest) and earn through halal means. "
            "Make du'a: 'Allahumma inni as'aluka min fadhlika' (O Allah, I ask You from Your bounty)."
        ),
        "Education": (
            "Begin studying with 'Bismillah ar-Rahman ar-Rahim'. "
            "Make du'a: 'Rabbi zidni ilma' (My Lord, increase me in knowledge). "
            "Pray two rak'ahs before exams seeking Allah's help. "
            "Study in a state of wudu and in a clean environment."
        ),
        "Relationships": (
            "Strengthen ties of kinship as commanded in the Quran. "
            "Practice forgiveness and patience. "
            "Give charity on behalf of strained relationships. "
            "Make du'a for reconciliation and understanding."
        ),
        "Travel": (
            "Recite the Traveler's Du'a before journeys. "
            "Pray two rak'ahs before travel. "
            "Carry a copy of Surah Al-Kahf for Friday reading. "
            "Say 'Bismillah' and make du'a for safe travel."
        ),
        "Spirituality": (
            "Perform the five daily prayers on time. "
            "Wake for Tahajjud and make du'a in the last third of the night. "
            "Recite Quran daily with contemplation. "
            "Increase dhikr and remembrance of Allah throughout the day."
        ),
        "Property": (
            "Recite Ayat al-Kursi in your home for protection. "
            "Give charity when moving to a new place. "
            "Make du'a for barakah (blessing) in your dwelling. "
            "Maintain cleanliness and pray regularly in your home."
        ),
        "Legal": (
            "Pray Salat al-Hajah for resolution of legal matters. "
            "Give charity and fast for three days. "
            "Recite Surah Yusuf for help with difficult situations. "
            "Trust in Allah's justice and seek knowledgeable counsel."
        ),
        "General": (
            "Maintain the five daily prayers and remember Allah often. "
            "Give charity regularly and help those in need. "
            "Read Quran daily and follow the Sunnah. "
            "Practice patience, gratitude, and trust in Allah's plan."
        ),
    },
    "buddhist": {
        "Career": (
            "Practice mindfulness in your daily work. "
            "Meditate on Right Livelihood from the Noble Eightfold Path. "
            "Chant the Heart Sutra for wisdom in career decisions. "
            "Practice generosity (Dana) and offer service to others."
        ),
        "Health": (
            "Practice mindfulness meditation for healing. "
            "Chant the Medicine Buddha Mantra: 'Tayata Om Bekandze Bekandze Maha Bekandze Radza Samudgate Soha'. "
            "Cultivate compassion through Metta (loving-kindness) meditation. "
            "Follow the Middle Way in diet and lifestyle."
        ),
        "Marriage": (
            "Practice Metta meditation for your partner. "
            "Apply the Four Noble Truths to understand relationship suffering. "
            "Cultivate compassion, patience, and right speech. "
            "Meditate together and practice mindfulness in communication."
        ),
        "Finance": (
            "Practice non-attachment to material wealth. "
            "Give Dana (charitable giving) regularly. "
            "Meditate on the impermanence of material possessions. "
            "Follow Right Livelihood and earn through ethical means."
        ),
        "Education": (
            "Begin study with meditation to calm and focus the mind. "
            "Practice mindfulness while studying. "
            "Chant the Manjushri Mantra for wisdom: 'Om Ara Pa Ca Na Dhih'. "
            "Cultivate beginner's mind and approach learning with humility."
        ),
        "Relationships": (
            "Practice Metta meditation for all beings. "
            "Cultivate the Four Brahmaviharas: loving-kindness, compassion, empathetic joy, and equanimity. "
            "Practice right speech and mindful communication. "
            "Let go of attachment and expectations."
        ),
        "Travel": (
            "Practice mindfulness during travel. "
            "Chant protection mantras before journeys. "
            "Carry a small Buddha statue or prayer beads. "
            "View travel as a pilgrimage for spiritual growth."
        ),
        "Spirituality": (
            "Establish daily meditation practice. "
            "Study the Dharma regularly. "
            "Practice the Noble Eightfold Path in daily life. "
            "Join a Sangha (spiritual community) for support and guidance."
        ),
        "Property": (
            "Create a meditation space in your home. "
            "Place Buddha statues or images mindfully. "
            "Practice non-attachment to your dwelling. "
            "Keep your space clean and peaceful to support practice."
        ),
        "Legal": (
            "Practice equanimity and patience during legal challenges. "
            "Meditate on karma and cause-and-effect. "
            "Chant the Heart Sutra for wisdom. "
            "Seek right action and speak truth with compassion."
        ),
        "General": (
            "Maintain daily meditation practice. "
            "Follow the Five Precepts and Noble Eightfold Path. "
            "Practice mindfulness in all activities. "
            "Cultivate compassion, wisdom, and equanimity."
        ),
    },
    "jain": {
        "Career": (
            "Practice Ahimsa (non-violence) in all professional dealings. "
            "Follow Satya (truthfulness) in business and work. "
            "Recite Namokar Mantra before starting work. "
            "Practice Aparigraha (non-possessiveness) in career ambitions."
        ),
        "Health": (
            "Recite the Namokar Mantra 108 times daily. "
            "Practice Kayotsarga (meditation) for healing. "
            "Follow dietary restrictions and practice mindful eating. "
            "Visit Jain temples and participate in spiritual practices."
        ),
        "Marriage": (
            "Practice mutual respect and non-violence in relationships. "
            "Recite Namokar Mantra together. "
            "Follow Brahmacharya (celibacy/appropriate conduct) principles. "
            "Perform charitable acts together."
        ),
        "Finance": (
            "Practice Aparigraha (non-possessiveness) with wealth. "
            "Give Dana (charity) according to Jain principles. "
            "Earn through right livelihood avoiding harm. "
            "Recite Namokar Mantra and practice contentment."
        ),
        "Education": (
            "Begin studies by reciting Namokar Mantra. "
            "Practice Samyak Darshan (right perception) in learning. "
            "Study Jain scriptures alongside academic subjects. "
            "Follow discipline and practice Swadhyaya (self-study)."
        ),
        "Relationships": (
            "Practice Ahimsa in all relationships. "
            "Cultivate forgiveness through Kshama (forgiveness). "
            "Follow Satya (truthfulness) in communication. "
            "Practice Anekantavada (multiple perspectives) to understand others."
        ),
        "Travel": (
            "Recite Namokar Mantra before journeys. "
            "Practice Ahimsa even while traveling. "
            "Carry Jain symbols or texts for spiritual protection. "
            "Consider pilgrimages to Jain tirthas."
        ),
        "Spirituality": (
            "Practice Samayik (meditation) daily. "
            "Recite Namokar Mantra regularly. "
            "Follow the Five Great Vows (for ascetics) or Twelve Vows (for householders). "
            "Practice Pratikraman for reflection and repentance."
        ),
        "Property": (
            "Create a proper Puja room in your home. "
            "Practice non-attachment to property. "
            "Ensure your dwelling supports spiritual practice. "
            "Keep the home pure and suitable for worship."
        ),
        "Legal": (
            "Practice Satya (truthfulness) in legal matters. "
            "Recite Namokar Mantra for guidance. "
            "Seek resolution through Ahimsa and right conduct. "
            "Practice equanimity and acceptance of karma."
        ),
        "General": (
            "Follow the Five Great Vows or Twelve Vows. "
            "Recite Namokar Mantra daily. "
            "Practice Ahimsa, Satya, and Aparigraha. "
            "Engage in regular spiritual practices and charity."
        ),
    },
    "sikh": {
        "Career": (
            "Recite Japji Sahib daily in the morning. "
            "Practice Kirat Karni (honest work) and avoid dishonest means. "
            "Do Seva (selfless service) alongside your career. "
            "Remember Waheguru throughout your workday."
        ),
        "Health": (
            "Recite Sukhmani Sahib for peace and healing. "
            "Read Chaupai Sahib for protection and strength. "
            "Visit Gurdwara and take Karah Parshad. "
            "Practice Naam Simran (remembrance of God's name) for well-being."
        ),
        "Marriage": (
            "Read the Anand Karaj ceremony guidelines. "
            "Recite Ardas together daily. "
            "Practice equality and mutual respect as taught by the Gurus. "
            "Do Seva together at the Gurdwara."
        ),
        "Finance": (
            "Practice Vand Chakna (sharing with others). "
            "Earn through Kirat Karni (honest means). "
            "Give Dasvandh (10% of earnings) to charity. "
            "Recite Japji Sahib and trust in Waheguru's provision."
        ),
        "Education": (
            "Begin study with Mool Mantar. "
            "Recite Japji Sahib for mental clarity. "
            "Practice discipline and dedication to learning. "
            "Remember that knowledge should serve humanity."
        ),
        "Relationships": (
            "Practice equality and respect for all. "
            "Recite Guru Granth Sahib for guidance. "
            "Do Seva together to strengthen bonds. "
            "Follow the teachings of the Gurus on compassion and love."
        ),
        "Travel": (
            "Recite Chaupai Sahib before travel for protection. "
            "Remember Waheguru throughout your journey. "
            "Carry a Gutka (small prayer book) with you. "
            "Visit Gurdwaras during your travels when possible."
        ),
        "Spirituality": (
            "Recite the five Banis daily (Japji Sahib, Jaap Sahib, Tav-Prasad Savaiye, Chaupai Sahib, Anand Sahib). "
            "Practice Naam Simran continuously. "
            "Do Seva at the Gurdwara regularly. "
            "Study Guru Granth Sahib and follow the Gurus' teachings."
        ),
        "Property": (
            "Create a space for Guru Granth Sahib in your home. "
            "Practice non-attachment to material possessions. "
            "Use your property to serve others when possible. "
            "Recite Ardas when moving to a new home."
        ),
        "Legal": (
            "Practice truth and honesty in all matters. "
            "Recite Sukhmani Sahib for peace and clarity. "
            "Seek Sangat (community) support and guidance. "
            "Trust in Waheguru's justice and maintain your integrity."
        ),
        "General": (
            "Live by the three pillars: Naam Japna, Kirat Karni, Vand Chakna. "
            "Recite daily prayers (Nitnem). "
            "Do Seva regularly at the Gurdwara. "
            "Follow the teachings of the Guru Granth Sahib."
        ),
    },
    "secular": {
        "Career": (
            "Practice daily meditation or mindfulness for clarity. "
            "Set clear intentions and goals for your career path. "
            "Engage in continuous learning and skill development. "
            "Network authentically and help others in their careers."
        ),
        "Health": (
            "Practice daily meditation for stress reduction. "
            "Maintain a balanced diet and regular exercise routine. "
            "Use positive affirmations and visualization techniques. "
            "Prioritize sleep, hydration, and mental health."
        ),
        "Marriage": (
            "Practice active listening and open communication. "
            "Schedule regular quality time together. "
            "Express gratitude and appreciation daily. "
            "Consider couples counseling or relationship workshops."
        ),
        "Finance": (
            "Create and follow a budget with mindful spending. "
            "Practice gratitude for what you have. "
            "Give to causes you care about regularly. "
            "Visualize financial abundance and set realistic goals."
        ),
        "Education": (
            "Create a dedicated, organized study space. "
            "Practice mindfulness before studying to improve focus. "
            "Use the Pomodoro Technique for effective learning. "
            "Maintain a growth mindset and celebrate small wins."
        ),
        "Relationships": (
            "Practice empathy and active listening. "
            "Set healthy boundaries and communicate needs clearly. "
            "Express gratitude and appreciation regularly. "
            "Invest time in meaningful connections."
        ),
        "Travel": (
            "Plan mindfully and research your destinations. "
            "Practice presence and mindfulness during travel. "
            "Keep important documents organized and accessible. "
            "Embrace new experiences with an open mind."
        ),
        "Spirituality": (
            "Develop a daily meditation or mindfulness practice. "
            "Spend time in nature regularly. "
            "Journal for self-reflection and growth. "
            "Practice gratitude and connect with your inner self."
        ),
        "Property": (
            "Create spaces that support your well-being. "
            "Practice minimalism and declutter regularly. "
            "Use feng shui or space-clearing techniques. "
            "Make your home a reflection of your values."
        ),
        "Legal": (
            "Document everything thoroughly. "
            "Seek professional legal advice early. "
            "Practice stress-management techniques. "
            "Stay truthful and maintain your integrity."
        ),
        "General": (
            "Practice daily meditation or mindfulness. "
            "Cultivate gratitude and positive thinking. "
            "Help others and contribute to your community. "
            "Maintain balance in all areas of life."
        ),
    },
}


def get_remedy(category: str, religion: str = "hindu") -> str:
    """
    Fetch remedy text based on category and religion. 
    Defaults to Hindu remedies for backward compatibility.
    """
    # Normalize inputs
    religion = religion.lower() if religion else "hindu"
    category = category.strip().title() if category else "General"
    
    # Get religion-specific remedies
    religion_remedies = REMEDIES.get(religion, REMEDIES["secular"])
    
    # Return the appropriate remedy
    return religion_remedies.get(category, religion_remedies.get("General", "Practice mindfulness, maintain balance, and trust in your path."))
