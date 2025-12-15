class OrderBy:
    @staticmethod
    def newest_first():
        return "dateEntered desc"

    @staticmethod
    def oldest_first():
        return "dateEntered asc"

    @staticmethod
    def recently_updated():
        return "lastUpdated desc"
